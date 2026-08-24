from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable


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


class ActionLedger:
    """Tiny in-memory action identity store used only for the prototype.

    Production code should replace this with durable storage whose write/consume
    semantics are explicit. The prototype deliberately keeps the contract small.
    """

    def __init__(self, seen_action_ids: Iterable[str] | None = None) -> None:
        self._seen = set(seen_action_ids or [])

    def contains(self, action_id: str) -> bool:
        return action_id in self._seen

    def record(self, action_id: str) -> None:
        self._seen.add(action_id)


def _parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return parsed


def _evidence_ref(request: ActionRequest, verdict: str, reason_code: str) -> str:
    payload = {
        "actor": request.actor,
        "action": request.action,
        "target": request.target,
        "amount": str(request.amount),
        "action_id": request.action_id,
        "policy_version": request.policy_version,
        "checked_at": request.checked_at,
        "authorization_expires_at": request.authorization_expires_at,
        "execution_observed": request.execution_observed,
        "verdict": verdict,
        "reason_code": reason_code,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def verify_action(request: ActionRequest, policy: Policy, ledger: ActionLedger) -> Decision:
    """Evaluate one proposed financial action against one explicit policy snapshot.

    No wall-clock read occurs here. Freshness is derived only from timestamps in
    the request, so replaying the same evidence produces the same decision.
    """

    boundary = "EXECUTION_OBSERVED" if request.execution_observed else "EXTERNAL_UNVERIFIED"

    if request.policy_version != policy.version:
        verdict, reason = INCONCLUSIVE, "POLICY_VERSION_MISMATCH"
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
        ledger.record(request.action_id)

    return Decision(
        verdict=verdict,
        reason_code=reason,
        policy_version=policy.version,
        evidence_ref=_evidence_ref(request, verdict, reason),
        execution_boundary=boundary,
    )
