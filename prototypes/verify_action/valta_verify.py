from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal

from action_lifecycle import (
    ActionIdentityConflict,
    ActionLedger,
    ActionState,
    StateConflict,
)


ALLOW = "ALLOW"
BLOCK = "BLOCK"
INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class Policy:
    version: str
    allowed_actions: frozenset[str]
    allowed_targets: frozenset[str]
    max_amount: Decimal


@dataclass(frozen=True)
class ActionRequest:
    actor: str
    action: str
    target: str
    amount: Decimal
    action_id: str
    policy_version: str
    checked_at: str
    authorization_expires_at: str | None = None
    execution_observed: bool = False


@dataclass(frozen=True)
class Decision:
    verdict: str
    reason_code: str
    policy_version: str
    evidence_ref: str
    execution_boundary: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return parsed


def action_digest(request: ActionRequest) -> str:
    """Bind the durable action identity to the exact authorized business action.

    `checked_at` and `execution_observed` are evaluation/observation evidence, not
    mutable action parameters, so they are deliberately excluded from this digest.
    """

    payload = {
        "schema": "valta.action-request.v1",
        "actor": request.actor,
        "action": request.action,
        "target": request.target,
        "amount": str(request.amount),
        "action_id": request.action_id,
        "policy_version": request.policy_version,
        "authorization_expires_at": request.authorization_expires_at,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _evidence_ref(
    request: ActionRequest,
    action_ref: str,
    verdict: str,
    reason_code: str,
) -> str:
    payload = {
        "action_digest": action_ref,
        "checked_at": request.checked_at,
        "execution_observed": request.execution_observed,
        "verdict": verdict,
        "reason_code": reason_code,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _policy_decision(request: ActionRequest, policy: Policy) -> tuple[str, str]:
    if request.policy_version != policy.version:
        return INCONCLUSIVE, "POLICY_VERSION_MISMATCH"
    if request.authorization_expires_at is not None and _parse_iso(
        request.checked_at
    ) > _parse_iso(request.authorization_expires_at):
        return BLOCK, "STALE_AUTHORIZATION"
    if request.action not in policy.allowed_actions:
        return BLOCK, "ACTION_NOT_ALLOWED"
    if request.target not in policy.allowed_targets:
        return BLOCK, "TARGET_NOT_ALLOWED"
    if request.amount > policy.max_amount:
        return BLOCK, "AMOUNT_EXCEEDS_POLICY"
    if request.amount < Decimal("0"):
        return INCONCLUSIVE, "INVALID_NEGATIVE_AMOUNT"
    return ALLOW, "POLICY_SATISFIED"


def verify_action(request: ActionRequest, policy: Policy, ledger: ActionLedger) -> Decision:
    """Evaluate and durably record one policy decision without executing it.

    An `ALLOW` result leaves the action in `EVALUATED`; it does not consume the
    identity or prove execution. A caller must atomically reserve the current
    state/version before dispatching an external effect.

    No wall-clock read occurs here. Freshness is derived only from timestamps in
    the request, so replaying the same evidence produces the same decision.
    """

    action_ref = action_digest(request)
    boundary = (
        "CALLER_ASSERTED_EXECUTION"
        if request.execution_observed
        else "EXTERNAL_UNVERIFIED"
    )

    existing = ledger.get_optional(request.action_id)
    if existing is not None and existing.action_digest != action_ref:
        verdict, reason = BLOCK, "ACTION_ID_CONFLICT"
    elif existing is not None and existing.state in {
        ActionState.RESERVED.value,
        ActionState.DISPATCHING.value,
        ActionState.DISPATCHED.value,
        ActionState.OBSERVING.value,
        ActionState.VERIFIED.value,
        ActionState.UNVERIFIED.value,
        ActionState.RECONCILE_REQUIRED.value,
        ActionState.FINALIZED.value,
        ActionState.MANUAL_REVIEW_REQUIRED.value,
    }:
        verdict, reason = BLOCK, "DUPLICATE_ACTION_ID"
    else:
        verdict, reason = _policy_decision(request, policy)

    evidence_ref = _evidence_ref(request, action_ref, verdict, reason)
    decision = Decision(
        verdict=verdict,
        reason_code=reason,
        policy_version=policy.version,
        evidence_ref=evidence_ref,
        execution_boundary=boundary,
    )

    if reason not in {"ACTION_ID_CONFLICT", "DUPLICATE_ACTION_ID"}:
        try:
            ledger.record_decision(
                action_id=request.action_id,
                action_digest=action_ref,
                policy_version=policy.version,
                verdict=verdict,
                reason_code=reason,
                evidence_ref=evidence_ref,
                checked_at=request.checked_at,
            )
        except ActionIdentityConflict:
            # Another process may have bound the identity after our initial read.
            return Decision(
                verdict=BLOCK,
                reason_code="ACTION_ID_CONFLICT",
                policy_version=policy.version,
                evidence_ref=_evidence_ref(
                    request, action_ref, BLOCK, "ACTION_ID_CONFLICT"
                ),
                execution_boundary=boundary,
            )
        except StateConflict:
            # Another process may have reserved or advanced the action after our read.
            return Decision(
                verdict=BLOCK,
                reason_code="DUPLICATE_ACTION_ID",
                policy_version=policy.version,
                evidence_ref=_evidence_ref(
                    request, action_ref, BLOCK, "DUPLICATE_ACTION_ID"
                ),
                execution_boundary=boundary,
            )

    return decision
