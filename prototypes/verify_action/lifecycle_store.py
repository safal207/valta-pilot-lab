from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping

from lifecycle_types import (
    ACTIVE_IDENTITY_STATES,
    BLOCKED,
    CANCELLED_BEFORE_DISPATCH,
    DISPATCHED,
    DISPATCHING,
    DISPATCH_ACCEPTED,
    DISPATCH_REJECTED_NO_EFFECT,
    DISPATCH_UNKNOWN,
    EVALUATED,
    FINALIZED,
    FINAL_VERDICTS,
    INCONCLUSIVE_STATE,
    MANUAL_REVIEW_REQUIRED,
    OBSERVING,
    OBSERVATION_INCOMPLETE,
    OBSERVED_CONFLICT,
    OBSERVED_EXPECTED_EFFECT,
    OBSERVED_NO_EFFECT,
    PRE_RESERVATION_STATES,
    RECONCILE_REQUIRED,
    RELEASED_NO_EFFECT,
    RESERVED,
    UNVERIFIED,
    VERIFIED,
    ActionDigestMismatchError,
    ActionEvent,
    ActionNotFoundError,
    ActionRecord,
    EvidenceIntegrityError,
    StaleGenerationError,
    StaleVersionError,
    StateConflictError,
    UnsafeReleaseError,
    canonical_json,
    event_digest,
    validate_evidence_time,
    verify_and_replay_events,
)
from valta_verify import ALLOW, BLOCK, INCONCLUSIVE, ActionRequest, Decision, canonical_action_digest


class SQLiteActionStore:
    """Durable one-node MVP store with CAS versions and fencing generations.

    This protects a local dispatch boundary. End-to-end guarantees still depend
    on downstream idempotency and authoritative effect observation.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._lock = threading.RLock()
        self._db = sqlite3.connect(
            self.path, timeout=10.0, isolation_level=None, check_same_thread=False
        )
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA foreign_keys = ON")
        self._db.execute("PRAGMA journal_mode = WAL")
        self._db.execute("PRAGMA synchronous = FULL")
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS actions (
              action_id TEXT PRIMARY KEY, action_digest TEXT NOT NULL,
              state TEXT NOT NULL, version INTEGER NOT NULL CHECK(version >= 1),
              generation INTEGER NOT NULL CHECK(generation >= 0),
              decision_verdict TEXT, decision_reason_code TEXT,
              decision_evidence_ref TEXT, dispatch_status TEXT,
              observation_status TEXT, final_verdict TEXT
            );
            CREATE TABLE IF NOT EXISTS action_events (
              action_id TEXT NOT NULL, sequence INTEGER NOT NULL,
              event_type TEXT NOT NULL, from_state TEXT, to_state TEXT NOT NULL,
              version INTEGER NOT NULL, generation INTEGER NOT NULL,
              evidence_at TEXT NOT NULL, evidence_json TEXT NOT NULL,
              previous_event_digest TEXT, event_digest TEXT NOT NULL,
              PRIMARY KEY(action_id, sequence),
              FOREIGN KEY(action_id) REFERENCES actions(action_id)
            );
            """
        )

    def close(self) -> None:
        with self._lock:
            self._db.close()

    def __enter__(self) -> "SQLiteActionStore":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                yield self._db
            except Exception:
                self._db.execute("ROLLBACK")
                raise
            else:
                self._db.execute("COMMIT")

    @staticmethod
    def _record(row: sqlite3.Row) -> ActionRecord:
        return ActionRecord(**{key: row[key] for key in ActionRecord.__dataclass_fields__})

    def _row(self, db: sqlite3.Connection, action_id: str) -> sqlite3.Row:
        row = db.execute("SELECT * FROM actions WHERE action_id = ?", (action_id,)).fetchone()
        if row is None:
            raise ActionNotFoundError(f"unknown action_id: {action_id}")
        return row

    def get_action(self, action_id: str) -> ActionRecord:
        with self._lock:
            return self._record(self._row(self._db, action_id))

    def contains(self, action_id: str) -> bool:
        with self._lock:
            row = self._db.execute(
                "SELECT state FROM actions WHERE action_id = ?", (action_id,)
            ).fetchone()
            return row is not None and row["state"] in ACTIVE_IDENTITY_STATES

    def action_digest(self, action_id: str) -> str | None:
        with self._lock:
            row = self._db.execute(
                "SELECT action_digest FROM actions WHERE action_id = ?", (action_id,)
            ).fetchone()
            return None if row is None else str(row["action_digest"])

    def _append(
        self,
        db: sqlite3.Connection,
        *,
        current: ActionRecord | None,
        action_id: str,
        event_type: str,
        to_state: str,
        version: int,
        generation: int,
        evidence_at: str,
        evidence: Mapping[str, Any],
    ) -> None:
        validate_evidence_time(evidence_at)
        previous = db.execute(
            "SELECT sequence, event_digest FROM action_events WHERE action_id = ? "
            "ORDER BY sequence DESC LIMIT 1",
            (action_id,),
        ).fetchone()
        sequence = 1 if previous is None else int(previous["sequence"]) + 1
        previous_digest = None if previous is None else previous["event_digest"]
        digest = event_digest(
            action_id=action_id,
            sequence=sequence,
            event_type=event_type,
            from_state=None if current is None else current.state,
            to_state=to_state,
            version=version,
            generation=generation,
            evidence_at=evidence_at,
            evidence=evidence,
            previous_event_digest=previous_digest,
        )
        db.execute(
            "INSERT INTO action_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                action_id,
                sequence,
                event_type,
                None if current is None else current.state,
                to_state,
                version,
                generation,
                evidence_at,
                canonical_json(dict(evidence)),
                previous_digest,
                digest,
            ),
        )

    def _load(
        self,
        db: sqlite3.Connection,
        action_id: str,
        expected_version: int,
        allowed_states: frozenset[str],
        generation: int | None = None,
    ) -> ActionRecord:
        current = self._record(self._row(db, action_id))
        if current.version != expected_version:
            raise StaleVersionError(
                f"expected version {expected_version}, found {current.version}"
            )
        if current.state not in allowed_states:
            raise StateConflictError(f"state {current.state} cannot perform this transition")
        if generation is not None and current.generation != generation:
            raise StaleGenerationError(
                f"expected generation {generation}, found {current.generation}"
            )
        return current

    def _apply(
        self,
        db: sqlite3.Connection,
        current: ActionRecord,
        *,
        to_state: str,
        event_type: str,
        evidence_at: str,
        evidence: Mapping[str, Any],
        generation: int | None = None,
        dispatch_status: str | None | object = ...,
        observation_status: str | None | object = ...,
        final_verdict: str | None | object = ...,
    ) -> ActionRecord:
        version = current.version + 1
        generation = current.generation if generation is None else generation
        dispatch = current.dispatch_status if dispatch_status is ... else dispatch_status
        observation = (
            current.observation_status if observation_status is ... else observation_status
        )
        final = current.final_verdict if final_verdict is ... else final_verdict
        changed = db.execute(
            "UPDATE actions SET state=?, version=?, generation=?, dispatch_status=?, "
            "observation_status=?, final_verdict=? WHERE action_id=? AND version=?",
            (
                to_state,
                version,
                generation,
                dispatch,
                observation,
                final,
                current.action_id,
                current.version,
            ),
        )
        if changed.rowcount != 1:
            raise StaleVersionError("transition lost an expected-version race")
        self._append(
            db,
            current=current,
            action_id=current.action_id,
            event_type=event_type,
            to_state=to_state,
            version=version,
            generation=generation,
            evidence_at=evidence_at,
            evidence=evidence,
        )
        return self._record(self._row(db, current.action_id))

    def record_evaluation(self, request: ActionRequest, decision: Decision) -> ActionRecord:
        digest = canonical_action_digest(request)
        if decision.action_digest != digest:
            raise ActionDigestMismatchError("decision is not bound to the supplied action")
        states = {ALLOW: EVALUATED, BLOCK: BLOCKED, INCONCLUSIVE: INCONCLUSIVE_STATE}
        if decision.verdict not in states:
            raise ValueError(f"unsupported decision verdict: {decision.verdict}")
        target = states[decision.verdict]
        evidence = {
            "decision": decision.to_dict(),
            "checked_at": request.checked_at,
            "authorization_expires_at": request.authorization_expires_at,
        }

        with self._tx() as db:
            row = db.execute(
                "SELECT * FROM actions WHERE action_id = ?", (request.action_id,)
            ).fetchone()
            if row is None:
                db.execute(
                    "INSERT INTO actions VALUES (?, ?, ?, 1, 0, ?, ?, ?, NULL, NULL, NULL)",
                    (
                        request.action_id,
                        digest,
                        target,
                        decision.verdict,
                        decision.reason_code,
                        decision.evidence_ref,
                    ),
                )
                self._append(
                    db,
                    current=None,
                    action_id=request.action_id,
                    event_type="DECISION_RECORDED",
                    to_state=target,
                    version=1,
                    generation=0,
                    evidence_at=request.checked_at,
                    evidence=evidence,
                )
                return self._record(self._row(db, request.action_id))

            current = self._record(row)
            if current.action_digest != digest:
                raise ActionDigestMismatchError(
                    "action_id is already bound to a different action digest"
                )
            if current.state not in PRE_RESERVATION_STATES:
                raise StateConflictError(
                    f"cannot record a fresh evaluation from state {current.state}"
                )
            if (
                current.state == target
                and current.decision_verdict == decision.verdict
                and current.decision_reason_code == decision.reason_code
                and current.decision_evidence_ref == decision.evidence_ref
            ):
                return current

            version = current.version + 1
            changed = db.execute(
                "UPDATE actions SET state=?, version=?, decision_verdict=?, "
                "decision_reason_code=?, decision_evidence_ref=?, dispatch_status=NULL, "
                "observation_status=NULL, final_verdict=NULL "
                "WHERE action_id=? AND version=?",
                (
                    target,
                    version,
                    decision.verdict,
                    decision.reason_code,
                    decision.evidence_ref,
                    request.action_id,
                    current.version,
                ),
            )
            if changed.rowcount != 1:
                raise StaleVersionError("evaluation lost an expected-version race")
            self._append(
                db,
                current=current,
                action_id=request.action_id,
                event_type="DECISION_RECORDED",
                to_state=target,
                version=version,
                generation=current.generation,
                evidence_at=request.checked_at,
                evidence=evidence,
            )
            return self._record(self._row(db, request.action_id))

    def reserve(
        self,
        action_id: str,
        *,
        expected_version: int,
        evidence_at: str,
        evidence: Mapping[str, Any] | None = None,
    ) -> ActionRecord:
        with self._tx() as db:
            current = self._load(db, action_id, expected_version, frozenset({EVALUATED}))
            if current.decision_verdict != ALLOW:
                raise StateConflictError("only an ALLOW decision may be reserved")
            return self._apply(
                db,
                current,
                to_state=RESERVED,
                event_type="ACTION_RESERVED",
                evidence_at=evidence_at,
                evidence=dict(evidence or {}),
                generation=current.generation + 1,
                dispatch_status=None,
                observation_status=None,
                final_verdict=None,
            )

    def mark_dispatching(
        self,
        action_id: str,
        *,
        expected_version: int,
        generation: int,
        evidence_at: str,
        adapter: str,
        downstream_idempotency_key: str | None = None,
    ) -> ActionRecord:
        with self._tx() as db:
            current = self._load(
                db, action_id, expected_version, frozenset({RESERVED}), generation
            )
            return self._apply(
                db,
                current,
                to_state=DISPATCHING,
                event_type="DISPATCH_STARTED",
                evidence_at=evidence_at,
                evidence={
                    "adapter": adapter,
                    "downstream_idempotency_key": downstream_idempotency_key,
                },
            )

    def record_dispatch_result(
        self,
        action_id: str,
        *,
        expected_version: int,
        generation: int,
        evidence_at: str,
        status: str,
        downstream_request_id: str | None = None,
        evidence: Mapping[str, Any] | None = None,
    ) -> ActionRecord:
        targets = {
            DISPATCH_ACCEPTED: DISPATCHED,
            DISPATCH_REJECTED_NO_EFFECT: RELEASED_NO_EFFECT,
            DISPATCH_UNKNOWN: RECONCILE_REQUIRED,
        }
        if status not in targets:
            raise ValueError(f"unsupported dispatch status: {status}")
        with self._tx() as db:
            current = self._load(
                db, action_id, expected_version, frozenset({DISPATCHING}), generation
            )
            payload = dict(evidence or {})
            payload.update(
                {"dispatch_status": status, "downstream_request_id": downstream_request_id}
            )
            return self._apply(
                db,
                current,
                to_state=targets[status],
                event_type="DISPATCH_RESULT_RECORDED",
                evidence_at=evidence_at,
                evidence=payload,
                dispatch_status=status,
            )

    def begin_observation(
        self,
        action_id: str,
        *,
        expected_version: int,
        generation: int,
        evidence_at: str,
        evidence_source: str,
    ) -> ActionRecord:
        with self._tx() as db:
            current = self._load(
                db,
                action_id,
                expected_version,
                frozenset({DISPATCHED, RECONCILE_REQUIRED}),
                generation,
            )
            return self._apply(
                db,
                current,
                to_state=OBSERVING,
                event_type="OBSERVATION_STARTED",
                evidence_at=evidence_at,
                evidence={"evidence_source": evidence_source},
            )

    def record_observation(
        self,
        action_id: str,
        *,
        expected_version: int,
        generation: int,
        evidence_at: str,
        status: str,
        evidence_source: str,
        evidence: Mapping[str, Any],
    ) -> ActionRecord:
        targets = {
            OBSERVED_EXPECTED_EFFECT: VERIFIED,
            OBSERVED_NO_EFFECT: UNVERIFIED,
            OBSERVATION_INCOMPLETE: RECONCILE_REQUIRED,
            OBSERVED_CONFLICT: MANUAL_REVIEW_REQUIRED,
        }
        if status not in targets:
            raise ValueError(f"unsupported observation status: {status}")
        with self._tx() as db:
            current = self._load(
                db, action_id, expected_version, frozenset({OBSERVING}), generation
            )
            payload = dict(evidence)
            payload.update(
                {"observation_status": status, "evidence_source": evidence_source}
            )
            return self._apply(
                db,
                current,
                to_state=targets[status],
                event_type="EFFECT_OBSERVED",
                evidence_at=evidence_at,
                evidence=payload,
                observation_status=status,
            )

    def release_no_effect(
        self,
        action_id: str,
        *,
        expected_version: int,
        generation: int,
        evidence_at: str,
        known_no_effect: bool,
        evidence: Mapping[str, Any],
    ) -> ActionRecord:
        if not known_no_effect or not evidence:
            raise UnsafeReleaseError(
                "release requires explicit evidence that no external effect occurred"
            )
        with self._tx() as db:
            current = self._load(
                db, action_id, expected_version, frozenset({RESERVED}), generation
            )
            return self._apply(
                db,
                current,
                to_state=RELEASED_NO_EFFECT,
                event_type="RESERVATION_RELEASED_NO_EFFECT",
                evidence_at=evidence_at,
                evidence={"known_no_effect": True, **dict(evidence)},
                dispatch_status=None,
                observation_status=OBSERVED_NO_EFFECT,
                final_verdict=None,
            )

    def finalize(
        self,
        action_id: str,
        *,
        expected_version: int,
        generation: int,
        evidence_at: str,
        final_verdict: str,
        evidence: Mapping[str, Any] | None = None,
    ) -> ActionRecord:
        if final_verdict not in FINAL_VERDICTS:
            raise ValueError(f"unsupported final verdict: {final_verdict}")
        with self._tx() as db:
            current = self._load(
                db, action_id, expected_version, FINAL_VERDICTS, generation
            )
            if current.state != final_verdict:
                raise StateConflictError(
                    f"final verdict {final_verdict} does not match state {current.state}"
                )
            return self._apply(
                db,
                current,
                to_state=FINALIZED,
                event_type="ACTION_FINALIZED",
                evidence_at=evidence_at,
                evidence={"final_verdict": final_verdict, **dict(evidence or {})},
                final_verdict=final_verdict,
            )

    def history(self, action_id: str) -> list[ActionEvent]:
        with self._lock:
            self._row(self._db, action_id)
            rows = self._db.execute(
                "SELECT * FROM action_events WHERE action_id = ? ORDER BY sequence",
                (action_id,),
            ).fetchall()
        return [
            ActionEvent(
                action_id=row["action_id"],
                sequence=row["sequence"],
                event_type=row["event_type"],
                from_state=row["from_state"],
                to_state=row["to_state"],
                version=row["version"],
                generation=row["generation"],
                evidence_at=row["evidence_at"],
                evidence=json.loads(row["evidence_json"]),
                previous_event_digest=row["previous_event_digest"],
                event_digest=row["event_digest"],
            )
            for row in rows
        ]

    def verify_history(self, action_id: str) -> bool:
        if verify_and_replay_events(self.history(action_id)) != self.get_action(action_id).to_dict():
            raise EvidenceIntegrityError(
                "materialized action state does not match event replay"
            )
        return True

    def export_receipt(self, action_id: str) -> dict[str, Any]:
        self.verify_history(action_id)
        receipt: dict[str, Any] = {
            "schema_version": "verified-transition-receipt-v1",
            "guarantee_boundary": (
                "local durable reservation and fencing; downstream idempotency "
                "and observed-effect guarantees depend on adapter evidence"
            ),
            "action": self.get_action(action_id).to_dict(),
            "events": [event.to_dict() for event in self.history(action_id)],
        }
        receipt["receipt_digest"] = "sha256:" + hashlib.sha256(
            canonical_json(receipt).encode()
        ).hexdigest()
        return receipt
