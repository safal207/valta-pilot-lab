from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Mapping


__all__ = [
    "PROPOSED", "EVALUATED", "BLOCKED", "INCONCLUSIVE_STATE",
    "RESERVED", "DISPATCHING", "DISPATCHED", "OBSERVING",
    "VERIFIED", "UNVERIFIED", "RECONCILE_REQUIRED", "FINALIZED",
    "RESERVATION_EXPIRED", "RELEASED_NO_EFFECT",
    "CANCELLED_BEFORE_DISPATCH", "MANUAL_REVIEW_REQUIRED",
    "DISPATCH_ACCEPTED", "DISPATCH_REJECTED_NO_EFFECT", "DISPATCH_UNKNOWN",
    "OBSERVED_EXPECTED_EFFECT", "OBSERVED_NO_EFFECT",
    "OBSERVATION_INCOMPLETE", "OBSERVED_CONFLICT",
    "LifecycleError", "ActionNotFoundError", "ActionDigestMismatchError",
    "StateConflictError", "StaleVersionError", "StaleGenerationError",
    "UnsafeReleaseError", "EvidenceIntegrityError", "ActionRecord",
    "ActionEvent", "verify_receipt",
]

PROPOSED = "PROPOSED"
EVALUATED = "EVALUATED"
BLOCKED = "BLOCKED"
INCONCLUSIVE_STATE = "INCONCLUSIVE"
RESERVED = "RESERVED"
DISPATCHING = "DISPATCHING"
DISPATCHED = "DISPATCHED"
OBSERVING = "OBSERVING"
VERIFIED = "VERIFIED"
UNVERIFIED = "UNVERIFIED"
RECONCILE_REQUIRED = "RECONCILE_REQUIRED"
FINALIZED = "FINALIZED"
RESERVATION_EXPIRED = "RESERVATION_EXPIRED"
RELEASED_NO_EFFECT = "RELEASED_NO_EFFECT"
CANCELLED_BEFORE_DISPATCH = "CANCELLED_BEFORE_DISPATCH"
MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"

DISPATCH_ACCEPTED = "ACCEPTED"
DISPATCH_REJECTED_NO_EFFECT = "REJECTED_NO_EFFECT"
DISPATCH_UNKNOWN = "UNKNOWN"

OBSERVED_EXPECTED_EFFECT = "EXPECTED_EFFECT"
OBSERVED_NO_EFFECT = "NO_EFFECT"
OBSERVATION_INCOMPLETE = "INCOMPLETE"
OBSERVED_CONFLICT = "CONFLICT"

ACTIVE_IDENTITY_STATES = frozenset(
    {
        RESERVED,
        DISPATCHING,
        DISPATCHED,
        OBSERVING,
        VERIFIED,
        UNVERIFIED,
        RECONCILE_REQUIRED,
        MANUAL_REVIEW_REQUIRED,
        FINALIZED,
    }
)
PRE_RESERVATION_STATES = frozenset(
    {
        EVALUATED,
        BLOCKED,
        INCONCLUSIVE_STATE,
        RELEASED_NO_EFFECT,
        RESERVATION_EXPIRED,
        CANCELLED_BEFORE_DISPATCH,
    }
)
FINAL_VERDICTS = frozenset(
    {
        VERIFIED,
        UNVERIFIED,
        RECONCILE_REQUIRED,
        BLOCKED,
        INCONCLUSIVE_STATE,
        RELEASED_NO_EFFECT,
        CANCELLED_BEFORE_DISPATCH,
        MANUAL_REVIEW_REQUIRED,
    }
)


class LifecycleError(RuntimeError):
    """Base error for lifecycle state or evidence violations."""


class ActionNotFoundError(LifecycleError):
    pass


class ActionDigestMismatchError(LifecycleError):
    pass


class StateConflictError(LifecycleError):
    pass


class StaleVersionError(LifecycleError):
    pass


class StaleGenerationError(LifecycleError):
    pass


class UnsafeReleaseError(LifecycleError):
    pass


class EvidenceIntegrityError(LifecycleError):
    pass


@dataclass(frozen=True)
class ActionRecord:
    action_id: str
    action_digest: str
    state: str
    version: int
    generation: int
    decision_verdict: str | None
    decision_reason_code: str | None
    decision_evidence_ref: str | None
    dispatch_status: str | None
    observation_status: str | None
    final_verdict: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ActionEvent:
    action_id: str
    sequence: int
    event_type: str
    from_state: str | None
    to_state: str
    version: int
    generation: int
    evidence_at: str
    evidence: dict[str, Any]
    previous_event_digest: str | None
    event_digest: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_evidence_time(value: str) -> None:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("evidence timestamps must be timezone-aware")


def canonical_json(value: Mapping[str, Any] | dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def event_digest(
    *,
    action_id: str,
    sequence: int,
    event_type: str,
    from_state: str | None,
    to_state: str,
    version: int,
    generation: int,
    evidence_at: str,
    evidence: Mapping[str, Any],
    previous_event_digest: str | None,
) -> str:
    payload = {
        "action_id": action_id,
        "sequence": sequence,
        "event_type": event_type,
        "from_state": from_state,
        "to_state": to_state,
        "version": version,
        "generation": generation,
        "evidence_at": evidence_at,
        "evidence": dict(evidence),
        "previous_event_digest": previous_event_digest,
    }
    return "sha256:" + hashlib.sha256(canonical_json(payload).encode()).hexdigest()


def verify_and_replay_events(events: list[ActionEvent]) -> dict[str, Any]:
    if not events:
        raise EvidenceIntegrityError("action has no lifecycle events")

    action_id = events[0].action_id
    action_digest: str | None = None
    state: str | None = None
    version = generation = 0
    decision_verdict = decision_reason_code = decision_evidence_ref = None
    dispatch_status = observation_status = final_verdict = None
    previous_digest = previous_state = None

    for expected_sequence, event in enumerate(events, start=1):
        if event.action_id != action_id:
            raise EvidenceIntegrityError("receipt mixes action identities")
        if event.sequence != expected_sequence or event.version != expected_sequence:
            raise EvidenceIntegrityError("event sequence/version is not contiguous")
        if event.previous_event_digest != previous_digest:
            raise EvidenceIntegrityError("event previous digest mismatch")
        if event.from_state != previous_state:
            raise EvidenceIntegrityError("event state chain is discontinuous")
        expected_digest = event_digest(
            action_id=event.action_id,
            sequence=event.sequence,
            event_type=event.event_type,
            from_state=event.from_state,
            to_state=event.to_state,
            version=event.version,
            generation=event.generation,
            evidence_at=event.evidence_at,
            evidence=event.evidence,
            previous_event_digest=event.previous_event_digest,
        )
        if event.event_digest != expected_digest:
            raise EvidenceIntegrityError("event digest mismatch")

        if event.event_type == "DECISION_RECORDED":
            decision = event.evidence.get("decision")
            if not isinstance(decision, dict):
                raise EvidenceIntegrityError("decision evidence is missing")
            digest = decision.get("action_digest")
            if not isinstance(digest, str):
                raise EvidenceIntegrityError("decision action digest is missing")
            if action_digest is not None and action_digest != digest:
                raise EvidenceIntegrityError("action digest changed during replay")
            action_digest = digest
            decision_verdict = decision.get("verdict")
            decision_reason_code = decision.get("reason_code")
            decision_evidence_ref = decision.get("evidence_ref")
            dispatch_status = observation_status = final_verdict = None
        elif event.event_type == "DISPATCH_RESULT_RECORDED":
            dispatch_status = event.evidence.get("dispatch_status")
        elif event.event_type == "EFFECT_OBSERVED":
            observation_status = event.evidence.get("observation_status")
        elif event.event_type == "RESERVATION_RELEASED_NO_EFFECT":
            observation_status = OBSERVED_NO_EFFECT
        elif event.event_type == "ACTION_FINALIZED":
            final_verdict = event.evidence.get("final_verdict")

        state, version, generation = event.to_state, event.version, event.generation
        previous_digest, previous_state = event.event_digest, event.to_state

    if action_digest is None or state is None:
        raise EvidenceIntegrityError("events cannot reconstruct action state")
    return {
        "action_id": action_id,
        "action_digest": action_digest,
        "state": state,
        "version": version,
        "generation": generation,
        "decision_verdict": decision_verdict,
        "decision_reason_code": decision_reason_code,
        "decision_evidence_ref": decision_evidence_ref,
        "dispatch_status": dispatch_status,
        "observation_status": observation_status,
        "final_verdict": final_verdict,
    }


def verify_receipt(receipt: Mapping[str, Any]) -> bool:
    """Verify an exported receipt without the originating database."""

    if receipt.get("schema_version") != "verified-transition-receipt-v1":
        raise EvidenceIntegrityError("unsupported receipt schema")
    supplied_digest = receipt.get("receipt_digest")
    if not isinstance(supplied_digest, str):
        raise EvidenceIntegrityError("receipt digest is missing")
    unsigned = dict(receipt)
    unsigned.pop("receipt_digest", None)
    expected = "sha256:" + hashlib.sha256(canonical_json(unsigned).encode()).hexdigest()
    if supplied_digest != expected:
        raise EvidenceIntegrityError("receipt digest mismatch")

    values = receipt.get("events")
    if not isinstance(values, list):
        raise EvidenceIntegrityError("receipt events are missing")
    try:
        events = [ActionEvent(**value) for value in values if isinstance(value, dict)]
    except TypeError as exc:
        raise EvidenceIntegrityError("receipt event has an invalid shape") from exc
    if len(events) != len(values):
        raise EvidenceIntegrityError("receipt event is not an object")
    if verify_and_replay_events(events) != receipt.get("action"):
        raise EvidenceIntegrityError("receipt action does not match event replay")
    return True
