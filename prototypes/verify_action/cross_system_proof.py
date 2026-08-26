from __future__ import annotations

import hashlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from decimal import Decimal
from enum import Enum
from typing import Any

from action_lifecycle import (
    ActionLedger,
    ActionState,
    ConcurrencyConflict,
    StateConflict,
    verify_receipt_bundle,
)
from valta_verify import ActionRequest, Policy, action_digest, verify_action


class DispatchMode(str, Enum):
    SETTLED_AND_RECONCILED = "SETTLED_AND_RECONCILED"
    REJECTED_NO_EFFECT = "REJECTED_NO_EFFECT"
    ACCEPTED_NO_EFFECT = "ACCEPTED_NO_EFFECT"
    TIMEOUT_AFTER_RAIL_CREDIT = "TIMEOUT_AFTER_RAIL_CREDIT"


class ProofVerdict(str, Enum):
    VERIFIED = "VERIFIED"
    SAFE_TO_RETRY = "SAFE_TO_RETRY"
    UNVERIFIED = "UNVERIFIED"
    RECONCILE_REQUIRED = "RECONCILE_REQUIRED"


class StaleFenceError(RuntimeError):
    """Raised when an old execution generation reaches the provider boundary."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RailCredit:
    credit_id: str
    action_id: str
    recipient: str
    amount: str
    generation: int
    idempotency_key: str


@dataclass(frozen=True)
class LedgerPosting:
    posting_id: str
    action_id: str
    recipient: str
    amount: str
    generation: int
    rail_credit_id: str


@dataclass(frozen=True)
class ProviderOutcome:
    request_id: str
    action_id: str
    generation: int
    status: str
    response_lost: bool
    rail_credit_id: str | None = None
    ledger_posting_id: str | None = None


@dataclass(frozen=True)
class Observation:
    verdict: str
    evidence_ref: str
    provider_status: str
    provider_requests: int
    rail_effects: int
    ledger_effects: int
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["reasons"] = list(self.reasons)
        return value


@dataclass(frozen=True)
class ProofResult:
    scenario: str
    verdict: str
    decision_verdict: str
    lifecycle_state: str
    provider_status: str
    attempts: int
    reservation_winners: int
    rejected_attempts: int
    rail_effects: int
    ledger_effects: int
    economic_effects: int
    receipt_verified: bool
    receipt_digest: str
    observation_evidence_ref: str
    notes: tuple[str, ...]
    receipt_bundle: dict[str, Any]

    def to_dict(self, *, include_receipt: bool = True) -> dict[str, Any]:
        value = asdict(self)
        value["notes"] = list(self.notes)
        if not include_receipt:
            value.pop("receipt_bundle", None)
        return value


class SandboxRail:
    """External recipient rail with idempotency scoped to one declared key."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._by_key: dict[str, RailCredit] = {}

    def credit(
        self,
        *,
        action_id: str,
        recipient: str,
        amount: Decimal,
        generation: int,
        idempotency_key: str,
    ) -> RailCredit:
        with self._lock:
            existing = self._by_key.get(idempotency_key)
            if existing is not None:
                return existing
            credit = RailCredit(
                credit_id=f"rail:{action_id}:g{generation}",
                action_id=action_id,
                recipient=recipient,
                amount=str(amount),
                generation=generation,
                idempotency_key=idempotency_key,
            )
            self._by_key[idempotency_key] = credit
            return credit

    def credits_for(self, action_id: str) -> tuple[RailCredit, ...]:
        with self._lock:
            return tuple(
                credit for credit in self._by_key.values() if credit.action_id == action_id
            )


class SandboxAccountingLedger:
    """Customer ledger, intentionally separate from the provider and the rail."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._by_action: dict[str, LedgerPosting] = {}

    def post(
        self,
        *,
        action_id: str,
        recipient: str,
        amount: Decimal,
        generation: int,
        rail_credit_id: str,
    ) -> LedgerPosting:
        with self._lock:
            existing = self._by_action.get(action_id)
            if existing is not None:
                return existing
            posting = LedgerPosting(
                posting_id=f"ledger:{action_id}:g{generation}",
                action_id=action_id,
                recipient=recipient,
                amount=str(amount),
                generation=generation,
                rail_credit_id=rail_credit_id,
            )
            self._by_action[action_id] = posting
            return posting

    def postings_for(self, action_id: str) -> tuple[LedgerPosting, ...]:
        with self._lock:
            posting = self._by_action.get(action_id)
            return () if posting is None else (posting,)


class SandboxPaymentProvider:
    """Provider simulator that enforces the lifecycle fencing generation.

    Provider status is deliberately not treated as settlement proof. The observer
    reads provider, rail, and accounting state independently.
    """

    def __init__(
        self,
        *,
        rail: SandboxRail,
        ledger: SandboxAccountingLedger,
    ) -> None:
        self.rail = rail
        self.ledger = ledger
        self._lock = threading.RLock()
        self._latest_generation: dict[str, int] = {}
        self._outcomes: dict[tuple[str, int], ProviderOutcome] = {}

    def dispatch(
        self,
        *,
        request: ActionRequest,
        generation: int,
        fencing_token: str | None,
        mode: DispatchMode,
    ) -> ProviderOutcome:
        if fencing_token is None:
            raise ValueError("fencing_token is required")

        key = (request.action_id, generation)
        with self._lock:
            latest = self._latest_generation.get(request.action_id, 0)
            if generation < latest:
                raise StaleFenceError(
                    f"generation {generation} is stale; current generation is {latest}"
                )
            existing = self._outcomes.get(key)
            if existing is not None:
                return existing
            self._latest_generation[request.action_id] = generation

            request_id = f"provider:{request.action_id}:g{generation}"
            rail_credit: RailCredit | None = None
            ledger_posting: LedgerPosting | None = None

            if mode in {
                DispatchMode.SETTLED_AND_RECONCILED,
                DispatchMode.TIMEOUT_AFTER_RAIL_CREDIT,
            }:
                rail_credit = self.rail.credit(
                    action_id=request.action_id,
                    recipient=request.target,
                    amount=request.amount,
                    generation=generation,
                    idempotency_key=f"{request.action_id}:g{generation}",
                )

            if mode is DispatchMode.SETTLED_AND_RECONCILED:
                assert rail_credit is not None
                ledger_posting = self.ledger.post(
                    action_id=request.action_id,
                    recipient=request.target,
                    amount=request.amount,
                    generation=generation,
                    rail_credit_id=rail_credit.credit_id,
                )

            status = {
                DispatchMode.SETTLED_AND_RECONCILED: "ACCEPTED",
                DispatchMode.REJECTED_NO_EFFECT: "REJECTED_NO_EFFECT",
                DispatchMode.ACCEPTED_NO_EFFECT: "ACCEPTED",
                DispatchMode.TIMEOUT_AFTER_RAIL_CREDIT: "UNKNOWN",
            }[mode]
            outcome = ProviderOutcome(
                request_id=request_id,
                action_id=request.action_id,
                generation=generation,
                status=status,
                response_lost=mode is DispatchMode.TIMEOUT_AFTER_RAIL_CREDIT,
                rail_credit_id=None if rail_credit is None else rail_credit.credit_id,
                ledger_posting_id=(
                    None if ledger_posting is None else ledger_posting.posting_id
                ),
            )
            self._outcomes[key] = outcome
            return outcome

    def outcomes_for(self, action_id: str) -> tuple[ProviderOutcome, ...]:
        with self._lock:
            return tuple(
                outcome
                for (stored_action_id, _), outcome in sorted(self._outcomes.items())
                if stored_action_id == action_id
            )


class CrossSystemObserver:
    """Build one verdict from independent provider, rail, and ledger snapshots."""

    def __init__(
        self,
        *,
        provider: SandboxPaymentProvider,
        rail: SandboxRail,
        ledger: SandboxAccountingLedger,
    ) -> None:
        self.provider = provider
        self.rail = rail
        self.ledger = ledger

    def inspect(self, request: ActionRequest) -> Observation:
        provider_outcomes = self.provider.outcomes_for(request.action_id)
        rail_credits = self.rail.credits_for(request.action_id)
        ledger_postings = self.ledger.postings_for(request.action_id)
        provider_status = (
            "NO_PROVIDER_RECORD" if not provider_outcomes else provider_outcomes[-1].status
        )

        exact_rail = tuple(
            credit
            for credit in rail_credits
            if credit.recipient == request.target and credit.amount == str(request.amount)
        )
        exact_ledger = tuple(
            posting
            for posting in ledger_postings
            if posting.recipient == request.target and posting.amount == str(request.amount)
        )

        reasons: list[str] = []
        verdict: ProofVerdict
        if (
            provider_status == "REJECTED_NO_EFFECT"
            and not rail_credits
            and not ledger_postings
        ):
            verdict = ProofVerdict.SAFE_TO_RETRY
            reasons.append("provider proved rejection before any external effect")
        elif (
            len(exact_rail) == 1
            and len(exact_ledger) == 1
            and len(rail_credits) == 1
            and len(ledger_postings) == 1
            and exact_ledger[0].rail_credit_id == exact_rail[0].credit_id
        ):
            verdict = ProofVerdict.VERIFIED
            reasons.append("one matching rail credit and one linked ledger posting")
        elif provider_status == "ACCEPTED" and not rail_credits and not ledger_postings:
            verdict = ProofVerdict.UNVERIFIED
            reasons.append("provider accepted but no independent economic effect appeared")
        else:
            verdict = ProofVerdict.RECONCILE_REQUIRED
            if len(rail_credits) != len(ledger_postings):
                reasons.append("rail and ledger effect counts disagree")
            if len(rail_credits) > 1 or len(ledger_postings) > 1:
                reasons.append("multiple economic effects detected")
            if provider_status == "UNKNOWN":
                reasons.append("provider response was lost after dispatch")
            if not reasons:
                reasons.append("evidence is incomplete or conflicting")

        evidence_payload = {
            "schema": "valta.cross-system-observation.v1",
            "action_id": request.action_id,
            "expected": {
                "recipient": request.target,
                "amount": str(request.amount),
            },
            "provider": [asdict(outcome) for outcome in provider_outcomes],
            "rail": [asdict(credit) for credit in rail_credits],
            "ledger": [asdict(posting) for posting in ledger_postings],
            "verdict": verdict.value,
            "reasons": reasons,
        }
        return Observation(
            verdict=verdict.value,
            evidence_ref=_digest(evidence_payload),
            provider_status=provider_status,
            provider_requests=len(provider_outcomes),
            rail_effects=len(rail_credits),
            ledger_effects=len(ledger_postings),
            reasons=tuple(reasons),
        )


def default_policy() -> Policy:
    return Policy(
        version="payout-policy-v1",
        allowed_actions=frozenset({"release_payout"}),
        allowed_targets=frozenset({"creator-218"}),
        max_amount=Decimal("10000.00"),
    )


def payout_request(action_id: str) -> ActionRequest:
    return ActionRequest(
        actor="payout-agent",
        action="release_payout",
        target="creator-218",
        amount=Decimal("5000.00"),
        action_id=action_id,
        policy_version="payout-policy-v1",
        checked_at="2026-08-26T10:00:00+00:00",
        authorization_expires_at="2026-08-26T11:00:00+00:00",
    )


def _apply_observation(
    *,
    store: ActionLedger,
    request: ActionRequest,
    record: Any,
    observation: Observation,
) -> Any:
    if observation.verdict == ProofVerdict.SAFE_TO_RETRY.value:
        return record

    if record.state == ActionState.DISPATCHED.value:
        record = store.begin_observation(
            action_id=request.action_id,
            expected_version=record.version,
            generation=record.generation,
            observed_at="2026-08-26T10:02:20+00:00",
        )

    status = {
        ProofVerdict.VERIFIED.value: "MATCHED",
        ProofVerdict.UNVERIFIED.value: "ABSENT",
        ProofVerdict.RECONCILE_REQUIRED.value: "CONFLICT",
    }[observation.verdict]
    record = store.record_observation(
        action_id=request.action_id,
        expected_version=record.version,
        generation=record.generation,
        status=status,
        observed_at="2026-08-26T10:02:30+00:00",
        evidence_ref=observation.evidence_ref,
    )

    if observation.verdict in {
        ProofVerdict.VERIFIED.value,
        ProofVerdict.UNVERIFIED.value,
    }:
        record = store.finalize_if_version_matches(
            action_id=request.action_id,
            expected_version=record.version,
            generation=record.generation,
            finalized_at="2026-08-26T10:02:40+00:00",
            final_verdict=observation.verdict,
        )
    return record


def run_scenario(
    mode: DispatchMode,
    *,
    action_id: str,
    attempts: int = 1,
) -> ProofResult:
    if attempts < 1:
        raise ValueError("attempts must be positive")

    request = payout_request(action_id)
    policy = default_policy()
    store = ActionLedger()
    rail = SandboxRail()
    accounting = SandboxAccountingLedger()
    provider = SandboxPaymentProvider(rail=rail, ledger=accounting)
    observer = CrossSystemObserver(provider=provider, rail=rail, ledger=accounting)

    try:
        decision = verify_action(request, policy, store)
        if decision.verdict != "ALLOW":
            raise RuntimeError(f"demo request was not allowed: {decision.reason_code}")
        evaluated = store.get(action_id)

        reservation_winners = 0
        rejected_attempts = 0
        winning_record: Any | None = None

        def reserve_once() -> Any:
            return store.reserve_if_version_matches(
                action_id=action_id,
                action_digest=action_digest(request),
                expected_version=evaluated.version,
                reserved_at="2026-08-26T10:01:00+00:00",
                reservation_expires_at="2026-08-26T10:05:00+00:00",
            )

        if attempts == 1:
            winning_record = reserve_once()
            reservation_winners = 1
        else:
            with ThreadPoolExecutor(max_workers=attempts) as executor:
                futures = [executor.submit(reserve_once) for _ in range(attempts)]
                for future in futures:
                    try:
                        winning_record = future.result()
                        reservation_winners += 1
                    except (ConcurrencyConflict, StateConflict):
                        rejected_attempts += 1

        if winning_record is None or reservation_winners != 1:
            raise RuntimeError(
                f"expected one reservation owner, got {reservation_winners}"
            )

        dispatching = store.mark_dispatch_started(
            action_id=action_id,
            expected_version=winning_record.version,
            generation=winning_record.generation,
            started_at="2026-08-26T10:02:00+00:00",
            adapter="sandbox-cross-system-provider",
            downstream_idempotency_key=action_id,
        )
        provider_outcome = provider.dispatch(
            request=request,
            generation=dispatching.generation,
            fencing_token=dispatching.fencing_token,
            mode=mode,
        )
        lifecycle_record = store.record_dispatch_result(
            action_id=action_id,
            expected_version=dispatching.version,
            generation=dispatching.generation,
            status=provider_outcome.status,
            observed_at="2026-08-26T10:02:10+00:00",
            downstream_request_id=provider_outcome.request_id,
        )
        observation = observer.inspect(request)
        lifecycle_record = _apply_observation(
            store=store,
            request=request,
            record=lifecycle_record,
            observation=observation,
        )

        receipt = store.export_receipt(action_id)
        receipt_verified = verify_receipt_bundle(receipt)
        return ProofResult(
            scenario=mode.value,
            verdict=observation.verdict,
            decision_verdict=decision.verdict,
            lifecycle_state=lifecycle_record.state,
            provider_status=observation.provider_status,
            attempts=attempts,
            reservation_winners=reservation_winners,
            rejected_attempts=rejected_attempts,
            rail_effects=observation.rail_effects,
            ledger_effects=observation.ledger_effects,
            economic_effects=observation.rail_effects,
            receipt_verified=receipt_verified,
            receipt_digest=receipt["bundle_digest"],
            observation_evidence_ref=observation.evidence_ref,
            notes=observation.reasons,
            receipt_bundle=receipt,
        )
    finally:
        store.close()


def run_named_scenario(name: str) -> ProofResult:
    mapping = {
        "verified": (DispatchMode.SETTLED_AND_RECONCILED, 1),
        "safe-to-retry": (DispatchMode.REJECTED_NO_EFFECT, 1),
        "unverified": (DispatchMode.ACCEPTED_NO_EFFECT, 1),
        "reconcile-required": (DispatchMode.TIMEOUT_AFTER_RAIL_CREDIT, 1),
        "concurrent-retry": (DispatchMode.SETTLED_AND_RECONCILED, 24),
    }
    try:
        mode, attempts = mapping[name]
    except KeyError as exc:
        raise ValueError(f"unsupported scenario: {name}") from exc
    return run_scenario(mode, action_id=f"demo-{name}", attempts=attempts)


def run_all_scenarios() -> list[ProofResult]:
    return [
        run_named_scenario("verified"),
        run_named_scenario("safe-to-retry"),
        run_named_scenario("unverified"),
        run_named_scenario("reconcile-required"),
        run_named_scenario("concurrent-retry"),
    ]
