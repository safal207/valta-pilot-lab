from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable, Protocol


ALLOW = "ALLOW"
BLOCK = "BLOCK"
INCONCLUSIVE = "INCONCLUSIVE"


class ActionIdentitySource(Protocol):
    """Read-only identity view used by the deterministic policy evaluator."""

    def contains(self, action_id: str) -> bool:
        ...


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
    action_digest: str
    evidence_ref: str
    execution_boundary: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


class ActionLedger:
    """Explicit in-memory action identity registry for tests and demonstrations.

    `verify_action` never writes to this registry. Evaluation and execution are
    different lifecycle steps: callers may record an identity only after their
    declared execution boundary has durably reserved or consumed it.

    Production pilot code should use `SQLiteActionStore` from
    `action_lifecycle.py`, which records explicit states and recovery evidence.
    """

    def __init__(self, seen_action_ids: Iterable[str] | None = None) -> None:
        self._seen = set(seen_action_ids or [])

    def contains(self, action_id: str) -> bool:
        return action_id in self._seen

    def record(self, action_id: str) -> None:
        self._seen.add(action_id)

    def action_digest(self, action_id: str) -> None:
        """Legacy registry knows identity consumption but not the bound digest."""

        return None


def _parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return parsed


def canonical_action_digest(request: ActionRequest) -> str:
    """Bind the immutable identity and authorization-relevant action fields.

    `checked_at` and `execution_observed` are evidence about an evaluation or an
    observation, not part of the economic action identity. Re-evaluating the
    same action at a later explicit evidence time therefore preserves the digest.
    """

    payload = {
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
    verdict: str,
    reason_code: str,
    action_digest: str,
) -> str:
    payload = {
        "action_digest": action_digest,
        "checked_at": request.checked_at,
        "execution_observed": request.execution_observed,
        "verdict": verdict,
        "reason_code": reason_code,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def verify_action(
    request: ActionRequest,
    policy: Policy,
    ledger: ActionIdentitySource,
) -> Decision:
    """Evaluate one proposed financial action against one explicit policy snapshot.

    No wall-clock read occurs here. Freshness is derived only from timestamps in
    the request, so replaying the same evidence produces the same decision.

    An `ALLOW` decision does not reserve, dispatch, consume, or finalize an
    action identity. Those effects belong to an explicit durable lifecycle.
    """

    boundary = "EXECUTION_OBSERVED" if request.execution_observed else "EXTERNAL_UNVERIFIED"
    action_digest = canonical_action_digest(request)
    digest_getter = getattr(ledger, "action_digest", None)
    existing_digest = digest_getter(request.action_id) if callable(digest_getter) else None

    if request.policy_version != policy.version:
        verdict, reason = INCONCLUSIVE, "POLICY_VERSION_MISMATCH"
    elif existing_digest is not None and existing_digest != action_digest:
        verdict, reason = BLOCK, "ACTION_DIGEST_MISMATCH"
    elif ledger.contains(request.action_id):
        verdict, reason = BLOCK, "DUPLICATE_ACTION_ID"
    elif request.authorization_expires_at is not None and _parse_iso(request.checked_at) > _parse_iso(
        request.authorization_expires_at
    ):
        verdict, reason = BLOCK, "STALE_AUTHORIZATION"
    elif request.action not in policy.allowed_actions:
        verdict, reason = BLOCK, "ACTION_NOT_ALLOWED"
    elif request.target not in policy.allowed_targets:
        verdict, reason = BLOCK, "TARGET_NOT_ALLOWED"
    elif request.amount > policy.max_amount:
        verdict, reason = BLOCK, "AMOUNT_EXCEEDS_POLICY"
    elif request.amount < Decimal("0"):
        verdict, reason = INCONCLUSIVE, "INVALID_NEGATIVE_AMOUNT"
    else:
        verdict, reason = ALLOW, "POLICY_SATISFIED"

    return Decision(
        verdict=verdict,
        reason_code=reason,
        policy_version=policy.version,
        action_digest=action_digest,
        evidence_ref=_evidence_ref(request, verdict, reason, action_digest),
        execution_boundary=boundary,
    )
