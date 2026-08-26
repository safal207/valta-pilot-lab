from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Iterator, Protocol


SCHEMA_VERSION = "valta.action-lifecycle.v1"


class ActionState(str, Enum):
    PROPOSED = "PROPOSED"
    EVALUATED = "EVALUATED"
    BLOCKED = "BLOCKED"
    INCONCLUSIVE = "INCONCLUSIVE"
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


class DispatchStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED_NO_EFFECT = "REJECTED_NO_EFFECT"
    UNKNOWN = "UNKNOWN"


class ObservationStatus(str, Enum):
    MATCHED = "MATCHED"
    ABSENT = "ABSENT"
    CONFLICT = "CONFLICT"
    UNKNOWN = "UNKNOWN"


class LifecycleError(RuntimeError):
    """Base error for invalid or unsafe lifecycle operations."""


class ActionNotFound(LifecycleError):
    pass


class ActionIdentityConflict(LifecycleError):
    pass


class StateConflict(LifecycleError):
    pass


class ConcurrencyConflict(LifecycleError):
    pass


class ReservationExpired(StateConflict):
    pass


def _parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return parsed


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    encoded = _canonical_json(value).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _fencing_token(action_id: str, action_digest: str, generation: int) -> str | None:
    if generation <= 0:
        return None
    return _sha256(
        {
            "schema": "valta.fence.v1",
            "action_id": action_id,
            "action_digest": action_digest,
            "generation": generation,
        }
    )


@dataclass(frozen=True)
class ActionRecord:
    action_id: str
    action_digest: str
    state: str
    version: int
    generation: int
    policy_version: str
    decision: dict[str, str]
    reservation_expires_at: str | None
    dispatch_status: str | None
    final_verdict: str | None
    updated_at: str
    last_event_digest: str

    @property
    def fencing_token(self) -> str | None:
        return _fencing_token(self.action_id, self.action_digest, self.generation)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["fencing_token"] = self.fencing_token
        return value


@dataclass(frozen=True)
class LifecycleEvent:
    action_id: str
    sequence: int
    event_type: str
    from_state: str | None
    to_state: str
    version: int
    generation: int
    at: str
    evidence: dict[str, Any]
    previous_digest: str | None
    event_digest: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ActionStore(Protocol):
    def get(self, action_id: str) -> ActionRecord: ...

    def get_optional(self, action_id: str) -> ActionRecord | None: ...

    def record_decision(
        self,
        *,
        action_id: str,
        action_digest: str,
        policy_version: str,
        verdict: str,
        reason_code: str,
        evidence_ref: str,
        checked_at: str,
    ) -> ActionRecord: ...

    def reserve_if_version_matches(
        self,
        *,
        action_id: str,
        action_digest: str,
        expected_version: int,
        reserved_at: str,
        reservation_expires_at: str,
    ) -> ActionRecord: ...


_REEVALUATABLE_STATES = {
    ActionState.EVALUATED.value,
    ActionState.BLOCKED.value,
    ActionState.INCONCLUSIVE.value,
    ActionState.RESERVATION_EXPIRED.value,
    ActionState.RELEASED_NO_EFFECT.value,
    ActionState.CANCELLED_BEFORE_DISPATCH.value,
}

_ACTIVE_OR_CONSUMED_STATES = {
    ActionState.RESERVED.value,
    ActionState.DISPATCHING.value,
    ActionState.DISPATCHED.value,
    ActionState.OBSERVING.value,
    ActionState.VERIFIED.value,
    ActionState.UNVERIFIED.value,
    ActionState.RECONCILE_REQUIRED.value,
    ActionState.FINALIZED.value,
    ActionState.MANUAL_REVIEW_REQUIRED.value,
}


class SQLiteActionStore:
    """Transactional lifecycle store with explicit state/version fencing.

    The store never reads the wall clock. Every transition receives its evidence
    timestamp from the caller, so exported history is replayable and deterministic.
    """

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self.db_path = str(db_path)
        if self.db_path != ":memory:":
            Path(self.db_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(
            self.db_path,
            isolation_level=None,
            check_same_thread=False,
            timeout=30.0,
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.execute("PRAGMA busy_timeout = 30000")
        if self.db_path != ":memory:":
            self._conn.execute("PRAGMA journal_mode = WAL")
            self._conn.execute("PRAGMA synchronous = FULL")
        self._initialize_schema()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def __enter__(self) -> SQLiteActionStore:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _initialize_schema(self) -> None:
        with self._lock:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS actions (
                    action_id TEXT PRIMARY KEY,
                    action_digest TEXT NOT NULL,
                    state TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    generation INTEGER NOT NULL,
                    policy_version TEXT NOT NULL,
                    decision_json TEXT NOT NULL,
                    reservation_expires_at TEXT,
                    dispatch_status TEXT,
                    final_verdict TEXT,
                    updated_at TEXT NOT NULL,
                    last_event_digest TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS lifecycle_events (
                    action_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    from_state TEXT,
                    to_state TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    generation INTEGER NOT NULL,
                    at TEXT NOT NULL,
                    evidence_json TEXT NOT NULL,
                    previous_digest TEXT,
                    event_digest TEXT NOT NULL,
                    PRIMARY KEY (action_id, sequence),
                    FOREIGN KEY (action_id) REFERENCES actions(action_id)
                );
                """
            )

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            self._conn.execute("BEGIN IMMEDIATE")
            try:
                yield self._conn
            except Exception:
                self._conn.execute("ROLLBACK")
                raise
            else:
                self._conn.execute("COMMIT")

    @staticmethod
    def _record_from_row(row: sqlite3.Row) -> ActionRecord:
        return ActionRecord(
            action_id=row["action_id"],
            action_digest=row["action_digest"],
            state=row["state"],
            version=row["version"],
            generation=row["generation"],
            policy_version=row["policy_version"],
            decision=json.loads(row["decision_json"]),
            reservation_expires_at=row["reservation_expires_at"],
            dispatch_status=row["dispatch_status"],
            final_verdict=row["final_verdict"],
            updated_at=row["updated_at"],
            last_event_digest=row["last_event_digest"],
        )

    @staticmethod
    def _event_from_row(row: sqlite3.Row) -> LifecycleEvent:
        return LifecycleEvent(
            action_id=row["action_id"],
            sequence=row["sequence"],
            event_type=row["event_type"],
            from_state=row["from_state"],
            to_state=row["to_state"],
            version=row["version"],
            generation=row["generation"],
            at=row["at"],
            evidence=json.loads(row["evidence_json"]),
            previous_digest=row["previous_digest"],
            event_digest=row["event_digest"],
        )

    @staticmethod
    def _fetch_row(conn: sqlite3.Connection, action_id: str) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM actions WHERE action_id = ?", (action_id,)).fetchone()
        if row is None:
            raise ActionNotFound(action_id)
        return row

    @staticmethod
    def _assert_identity(row: sqlite3.Row, action_digest: str) -> None:
        if row["action_digest"] != action_digest:
            raise ActionIdentityConflict(
                f"action_id {row['action_id']!r} is already bound to a different action digest"
            )

    @staticmethod
    def _assert_version_and_generation(
        row: sqlite3.Row,
        *,
        expected_version: int,
        generation: int | None = None,
    ) -> None:
        if row["version"] != expected_version:
            raise ConcurrencyConflict(
                f"stale version for {row['action_id']}: expected {expected_version}, "
                f"current {row['version']}"
            )
        if generation is not None and row["generation"] != generation:
            raise ConcurrencyConflict(
                f"stale fencing generation for {row['action_id']}: expected {generation}, "
                f"current {row['generation']}"
            )

    def _append_event(
        self,
        conn: sqlite3.Connection,
        *,
        action_id: str,
        event_type: str,
        from_state: str | None,
        to_state: str,
        version: int,
        generation: int,
        at: str,
        evidence: dict[str, Any],
    ) -> str:
        _parse_iso(at)
        row = self._fetch_row(conn, action_id)
        sequence = conn.execute(
            "SELECT COALESCE(MAX(sequence), 0) + 1 AS next_sequence "
            "FROM lifecycle_events WHERE action_id = ?",
            (action_id,),
        ).fetchone()["next_sequence"]
        previous_digest = row["last_event_digest"] or None
        payload = {
            "action_id": action_id,
            "sequence": sequence,
            "event_type": event_type,
            "from_state": from_state,
            "to_state": to_state,
            "version": version,
            "generation": generation,
            "at": at,
            "evidence": evidence,
            "previous_digest": previous_digest,
        }
        event_digest = _sha256(payload)
        conn.execute(
            """
            INSERT INTO lifecycle_events (
                action_id, sequence, event_type, from_state, to_state, version,
                generation, at, evidence_json, previous_digest, event_digest
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                action_id,
                sequence,
                event_type,
                from_state,
                to_state,
                version,
                generation,
                at,
                _canonical_json(evidence),
                previous_digest,
                event_digest,
            ),
        )
        conn.execute(
            "UPDATE actions SET last_event_digest = ? WHERE action_id = ?",
            (event_digest, action_id),
        )
        return event_digest

    def get(self, action_id: str) -> ActionRecord:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM actions WHERE action_id = ?", (action_id,)
            ).fetchone()
        if row is None:
            raise ActionNotFound(action_id)
        return self._record_from_row(row)

    def get_optional(self, action_id: str) -> ActionRecord | None:
        try:
            return self.get(action_id)
        except ActionNotFound:
            return None

    def history(self, action_id: str) -> list[LifecycleEvent]:
        with self._lock:
            exists = self._conn.execute(
                "SELECT 1 FROM actions WHERE action_id = ?", (action_id,)
            ).fetchone()
            if exists is None:
                raise ActionNotFound(action_id)
            rows = self._conn.execute(
                "SELECT * FROM lifecycle_events WHERE action_id = ? ORDER BY sequence",
                (action_id,),
            ).fetchall()
        return [self._event_from_row(row) for row in rows]

    def record_decision(
        self,
        *,
        action_id: str,
        action_digest: str,
        policy_version: str,
        verdict: str,
        reason_code: str,
        evidence_ref: str,
        checked_at: str,
    ) -> ActionRecord:
        _parse_iso(checked_at)
        target_states = {
            "ALLOW": ActionState.EVALUATED.value,
            "BLOCK": ActionState.BLOCKED.value,
            "INCONCLUSIVE": ActionState.INCONCLUSIVE.value,
        }
        try:
            target_state = target_states[verdict]
        except KeyError as exc:
            raise ValueError(f"unsupported decision verdict: {verdict}") from exc

        decision = {
            "verdict": verdict,
            "reason_code": reason_code,
            "evidence_ref": evidence_ref,
        }

        with self._transaction() as conn:
            existing = conn.execute(
                "SELECT * FROM actions WHERE action_id = ?", (action_id,)
            ).fetchone()
            if existing is None:
                conn.execute(
                    """
                    INSERT INTO actions (
                        action_id, action_digest, state, version, generation,
                        policy_version, decision_json, reservation_expires_at,
                        dispatch_status, final_verdict, updated_at, last_event_digest
                    ) VALUES (?, ?, ?, 0, 0, ?, '{}', NULL, NULL, NULL, ?, '')
                    """,
                    (
                        action_id,
                        action_digest,
                        ActionState.PROPOSED.value,
                        policy_version,
                        checked_at,
                    ),
                )
                self._append_event(
                    conn,
                    action_id=action_id,
                    event_type="ACTION_PROPOSED",
                    from_state=None,
                    to_state=ActionState.PROPOSED.value,
                    version=0,
                    generation=0,
                    at=checked_at,
                    evidence={
                        "action_digest": action_digest,
                        "policy_version": policy_version,
                    },
                )
                conn.execute(
                    """
                    UPDATE actions
                    SET state = ?, version = 1, decision_json = ?, updated_at = ?
                    WHERE action_id = ?
                    """,
                    (target_state, _canonical_json(decision), checked_at, action_id),
                )
                self._append_event(
                    conn,
                    action_id=action_id,
                    event_type="ACTION_EVALUATED",
                    from_state=ActionState.PROPOSED.value,
                    to_state=target_state,
                    version=1,
                    generation=0,
                    at=checked_at,
                    evidence=decision,
                )
                return self._record_from_row(self._fetch_row(conn, action_id))

            self._assert_identity(existing, action_digest)
            if existing["state"] not in _REEVALUATABLE_STATES:
                raise StateConflict(
                    f"cannot evaluate {action_id!r} while state is {existing['state']}"
                )
            if (
                existing["state"] == target_state
                and json.loads(existing["decision_json"]) == decision
            ):
                return self._record_from_row(existing)

            new_version = existing["version"] + 1
            conn.execute(
                """
                UPDATE actions
                SET state = ?, version = ?, policy_version = ?, decision_json = ?,
                    reservation_expires_at = NULL, dispatch_status = NULL,
                    final_verdict = NULL, updated_at = ?
                WHERE action_id = ? AND version = ?
                """,
                (
                    target_state,
                    new_version,
                    policy_version,
                    _canonical_json(decision),
                    checked_at,
                    action_id,
                    existing["version"],
                ),
            )
            self._append_event(
                conn,
                action_id=action_id,
                event_type="ACTION_REEVALUATED",
                from_state=existing["state"],
                to_state=target_state,
                version=new_version,
                generation=existing["generation"],
                at=checked_at,
                evidence=decision,
            )
            return self._record_from_row(self._fetch_row(conn, action_id))

    def reserve_if_version_matches(
        self,
        *,
        action_id: str,
        action_digest: str,
        expected_version: int,
        reserved_at: str,
        reservation_expires_at: str,
    ) -> ActionRecord:
        reserved_time = _parse_iso(reserved_at)
        expiry_time = _parse_iso(reservation_expires_at)
        if expiry_time <= reserved_time:
            raise ValueError("reservation_expires_at must be after reserved_at")

        with self._transaction() as conn:
            row = self._fetch_row(conn, action_id)
            self._assert_identity(row, action_digest)
            self._assert_version_and_generation(row, expected_version=expected_version)
            if row["state"] != ActionState.EVALUATED.value:
                raise StateConflict(
                    f"cannot reserve {action_id!r} from state {row['state']}"
                )
            decision = json.loads(row["decision_json"])
            if decision.get("verdict") != "ALLOW":
                raise StateConflict(f"cannot reserve {action_id!r} without ALLOW")

            new_version = row["version"] + 1
            new_generation = row["generation"] + 1
            conn.execute(
                """
                UPDATE actions
                SET state = ?, version = ?, generation = ?,
                    reservation_expires_at = ?, dispatch_status = NULL,
                    final_verdict = NULL, updated_at = ?
                WHERE action_id = ? AND version = ?
                """,
                (
                    ActionState.RESERVED.value,
                    new_version,
                    new_generation,
                    reservation_expires_at,
                    reserved_at,
                    action_id,
                    row["version"],
                ),
            )
            self._append_event(
                conn,
                action_id=action_id,
                event_type="ACTION_RESERVED",
                from_state=row["state"],
                to_state=ActionState.RESERVED.value,
                version=new_version,
                generation=new_generation,
                at=reserved_at,
                evidence={
                    "reservation_expires_at": reservation_expires_at,
                    "fencing_token": _fencing_token(
                        action_id, action_digest, new_generation
                    ),
                },
            )
            return self._record_from_row(self._fetch_row(conn, action_id))

    def mark_dispatch_started(
        self,
        *,
        action_id: str,
        expected_version: int,
        generation: int,
        started_at: str,
        adapter: str,
        downstream_idempotency_key: str,
    ) -> ActionRecord:
        started_time = _parse_iso(started_at)
        if not adapter:
            raise ValueError("adapter is required")
        if not downstream_idempotency_key:
            raise ValueError("downstream_idempotency_key is required")

        with self._transaction() as conn:
            row = self._fetch_row(conn, action_id)
            self._assert_version_and_generation(
                row, expected_version=expected_version, generation=generation
            )
            if row["state"] != ActionState.RESERVED.value:
                raise StateConflict(
                    f"cannot start dispatch for {action_id!r} from state {row['state']}"
                )
            if row["reservation_expires_at"] is not None and started_time >= _parse_iso(
                row["reservation_expires_at"]
            ):
                raise ReservationExpired(action_id)

            new_version = row["version"] + 1
            conn.execute(
                """
                UPDATE actions
                SET state = ?, version = ?, updated_at = ?
                WHERE action_id = ? AND version = ? AND generation = ?
                """,
                (
                    ActionState.DISPATCHING.value,
                    new_version,
                    started_at,
                    action_id,
                    row["version"],
                    generation,
                ),
            )
            self._append_event(
                conn,
                action_id=action_id,
                event_type="DISPATCH_STARTED",
                from_state=row["state"],
                to_state=ActionState.DISPATCHING.value,
                version=new_version,
                generation=generation,
                at=started_at,
                evidence={
                    "adapter": adapter,
                    "downstream_idempotency_key": downstream_idempotency_key,
                },
            )
            return self._record_from_row(self._fetch_row(conn, action_id))

    def record_dispatch_result(
        self,
        *,
        action_id: str,
        expected_version: int,
        generation: int,
        status: str,
        observed_at: str,
        downstream_request_id: str | None = None,
    ) -> ActionRecord:
        _parse_iso(observed_at)
        try:
            normalized = DispatchStatus(status).value
        except ValueError as exc:
            raise ValueError(f"unsupported dispatch status: {status}") from exc
        target_state = {
            DispatchStatus.ACCEPTED.value: ActionState.DISPATCHED.value,
            DispatchStatus.REJECTED_NO_EFFECT.value: ActionState.RELEASED_NO_EFFECT.value,
            DispatchStatus.UNKNOWN.value: ActionState.RECONCILE_REQUIRED.value,
        }[normalized]

        with self._transaction() as conn:
            row = self._fetch_row(conn, action_id)
            self._assert_version_and_generation(
                row, expected_version=expected_version, generation=generation
            )
            if row["state"] != ActionState.DISPATCHING.value:
                raise StateConflict(
                    f"cannot record dispatch result for {action_id!r} from state {row['state']}"
                )

            new_version = row["version"] + 1
            conn.execute(
                """
                UPDATE actions
                SET state = ?, version = ?, dispatch_status = ?, updated_at = ?
                WHERE action_id = ? AND version = ? AND generation = ?
                """,
                (
                    target_state,
                    new_version,
                    normalized,
                    observed_at,
                    action_id,
                    row["version"],
                    generation,
                ),
            )
            self._append_event(
                conn,
                action_id=action_id,
                event_type="DISPATCH_RESULT_RECORDED",
                from_state=row["state"],
                to_state=target_state,
                version=new_version,
                generation=generation,
                at=observed_at,
                evidence={
                    "status": normalized,
                    "downstream_request_id": downstream_request_id,
                },
            )
            return self._record_from_row(self._fetch_row(conn, action_id))

    def begin_observation(
        self,
        *,
        action_id: str,
        expected_version: int,
        generation: int,
        observed_at: str,
    ) -> ActionRecord:
        _parse_iso(observed_at)
        with self._transaction() as conn:
            row = self._fetch_row(conn, action_id)
            self._assert_version_and_generation(
                row, expected_version=expected_version, generation=generation
            )
            if row["state"] != ActionState.DISPATCHED.value:
                raise StateConflict(
                    f"cannot begin observation for {action_id!r} from state {row['state']}"
                )
            new_version = row["version"] + 1
            conn.execute(
                """
                UPDATE actions
                SET state = ?, version = ?, updated_at = ?
                WHERE action_id = ? AND version = ? AND generation = ?
                """,
                (
                    ActionState.OBSERVING.value,
                    new_version,
                    observed_at,
                    action_id,
                    row["version"],
                    generation,
                ),
            )
            self._append_event(
                conn,
                action_id=action_id,
                event_type="OBSERVATION_STARTED",
                from_state=row["state"],
                to_state=ActionState.OBSERVING.value,
                version=new_version,
                generation=generation,
                at=observed_at,
                evidence={},
            )
            return self._record_from_row(self._fetch_row(conn, action_id))

    def record_observation(
        self,
        *,
        action_id: str,
        expected_version: int,
        generation: int,
        status: str,
        observed_at: str,
        evidence_ref: str,
    ) -> ActionRecord:
        _parse_iso(observed_at)
        if not evidence_ref:
            raise ValueError("evidence_ref is required")
        try:
            normalized = ObservationStatus(status).value
        except ValueError as exc:
            raise ValueError(f"unsupported observation status: {status}") from exc
        target_state = {
            ObservationStatus.MATCHED.value: ActionState.VERIFIED.value,
            ObservationStatus.ABSENT.value: ActionState.UNVERIFIED.value,
            ObservationStatus.CONFLICT.value: ActionState.RECONCILE_REQUIRED.value,
            ObservationStatus.UNKNOWN.value: ActionState.RECONCILE_REQUIRED.value,
        }[normalized]

        with self._transaction() as conn:
            row = self._fetch_row(conn, action_id)
            self._assert_version_and_generation(
                row, expected_version=expected_version, generation=generation
            )
            if row["state"] not in {
                ActionState.DISPATCHED.value,
                ActionState.OBSERVING.value,
                ActionState.RECONCILE_REQUIRED.value,
            }:
                raise StateConflict(
                    f"cannot record observation for {action_id!r} from state {row['state']}"
                )

            new_version = row["version"] + 1
            conn.execute(
                """
                UPDATE actions
                SET state = ?, version = ?, updated_at = ?
                WHERE action_id = ? AND version = ? AND generation = ?
                """,
                (
                    target_state,
                    new_version,
                    observed_at,
                    action_id,
                    row["version"],
                    generation,
                ),
            )
            self._append_event(
                conn,
                action_id=action_id,
                event_type="EFFECT_OBSERVED",
                from_state=row["state"],
                to_state=target_state,
                version=new_version,
                generation=generation,
                at=observed_at,
                evidence={"status": normalized, "evidence_ref": evidence_ref},
            )
            return self._record_from_row(self._fetch_row(conn, action_id))

    def finalize_if_version_matches(
        self,
        *,
        action_id: str,
        expected_version: int,
        generation: int,
        finalized_at: str,
        final_verdict: str,
    ) -> ActionRecord:
        _parse_iso(finalized_at)
        if final_verdict not in {
            ActionState.VERIFIED.value,
            ActionState.UNVERIFIED.value,
        }:
            raise ValueError("final_verdict must be VERIFIED or UNVERIFIED")

        with self._transaction() as conn:
            row = self._fetch_row(conn, action_id)
            self._assert_version_and_generation(
                row, expected_version=expected_version, generation=generation
            )
            if row["state"] != final_verdict:
                raise StateConflict(
                    f"cannot finalize {action_id!r} as {final_verdict} from state {row['state']}"
                )

            new_version = row["version"] + 1
            conn.execute(
                """
                UPDATE actions
                SET state = ?, version = ?, final_verdict = ?, updated_at = ?
                WHERE action_id = ? AND version = ? AND generation = ?
                """,
                (
                    ActionState.FINALIZED.value,
                    new_version,
                    final_verdict,
                    finalized_at,
                    action_id,
                    row["version"],
                    generation,
                ),
            )
            self._append_event(
                conn,
                action_id=action_id,
                event_type="ACTION_FINALIZED",
                from_state=row["state"],
                to_state=ActionState.FINALIZED.value,
                version=new_version,
                generation=generation,
                at=finalized_at,
                evidence={"final_verdict": final_verdict},
            )
            return self._record_from_row(self._fetch_row(conn, action_id))

    def expire_reservation(
        self,
        *,
        action_id: str,
        expected_version: int,
        generation: int,
        checked_at: str,
    ) -> ActionRecord:
        checked_time = _parse_iso(checked_at)
        with self._transaction() as conn:
            row = self._fetch_row(conn, action_id)
            self._assert_version_and_generation(
                row, expected_version=expected_version, generation=generation
            )
            if row["state"] != ActionState.RESERVED.value:
                raise StateConflict(
                    f"cannot expire reservation for {action_id!r} from state {row['state']}"
                )
            expires_at = row["reservation_expires_at"]
            if expires_at is None or checked_time < _parse_iso(expires_at):
                raise StateConflict("reservation is not expired at supplied evidence time")

            new_version = row["version"] + 1
            conn.execute(
                """
                UPDATE actions
                SET state = ?, version = ?, updated_at = ?
                WHERE action_id = ? AND version = ? AND generation = ?
                """,
                (
                    ActionState.RESERVATION_EXPIRED.value,
                    new_version,
                    checked_at,
                    action_id,
                    row["version"],
                    generation,
                ),
            )
            self._append_event(
                conn,
                action_id=action_id,
                event_type="RESERVATION_EXPIRED",
                from_state=row["state"],
                to_state=ActionState.RESERVATION_EXPIRED.value,
                version=new_version,
                generation=generation,
                at=checked_at,
                evidence={"reservation_expires_at": expires_at},
            )
            return self._record_from_row(self._fetch_row(conn, action_id))

    def release_if_safe(
        self,
        *,
        action_id: str,
        expected_version: int,
        generation: int,
        released_at: str,
        no_effect_evidence_ref: str,
    ) -> ActionRecord:
        _parse_iso(released_at)
        if not no_effect_evidence_ref:
            raise ValueError("no_effect_evidence_ref is required")

        with self._transaction() as conn:
            row = self._fetch_row(conn, action_id)
            self._assert_version_and_generation(
                row, expected_version=expected_version, generation=generation
            )
            if row["state"] not in {
                ActionState.RESERVED.value,
                ActionState.RESERVATION_EXPIRED.value,
            }:
                raise StateConflict(
                    f"cannot release {action_id!r} from state {row['state']}; "
                    "post-dispatch uncertainty requires reconciliation"
                )

            new_version = row["version"] + 1
            conn.execute(
                """
                UPDATE actions
                SET state = ?, version = ?, updated_at = ?
                WHERE action_id = ? AND version = ? AND generation = ?
                """,
                (
                    ActionState.RELEASED_NO_EFFECT.value,
                    new_version,
                    released_at,
                    action_id,
                    row["version"],
                    generation,
                ),
            )
            self._append_event(
                conn,
                action_id=action_id,
                event_type="RESERVATION_RELEASED_NO_EFFECT",
                from_state=row["state"],
                to_state=ActionState.RELEASED_NO_EFFECT.value,
                version=new_version,
                generation=generation,
                at=released_at,
                evidence={"no_effect_evidence_ref": no_effect_evidence_ref},
            )
            return self._record_from_row(self._fetch_row(conn, action_id))

    def recover_after_restart(
        self,
        *,
        action_id: str,
        expected_version: int,
        generation: int,
        recovered_at: str,
    ) -> ActionRecord:
        _parse_iso(recovered_at)
        with self._transaction() as conn:
            row = self._fetch_row(conn, action_id)
            self._assert_version_and_generation(
                row, expected_version=expected_version, generation=generation
            )
            if row["state"] == ActionState.RESERVED.value:
                return self._record_from_row(row)
            if row["state"] not in {
                ActionState.DISPATCHING.value,
                ActionState.DISPATCHED.value,
                ActionState.OBSERVING.value,
            }:
                return self._record_from_row(row)

            new_version = row["version"] + 1
            conn.execute(
                """
                UPDATE actions
                SET state = ?, version = ?, updated_at = ?
                WHERE action_id = ? AND version = ? AND generation = ?
                """,
                (
                    ActionState.RECONCILE_REQUIRED.value,
                    new_version,
                    recovered_at,
                    action_id,
                    row["version"],
                    generation,
                ),
            )
            self._append_event(
                conn,
                action_id=action_id,
                event_type="RESTART_RECOVERY_REQUIRES_RECONCILIATION",
                from_state=row["state"],
                to_state=ActionState.RECONCILE_REQUIRED.value,
                version=new_version,
                generation=generation,
                at=recovered_at,
                evidence={"reason": "outcome_not_proven_after_restart"},
            )
            return self._record_from_row(self._fetch_row(conn, action_id))

    def export_receipt(self, action_id: str) -> dict[str, Any]:
        action = self.get(action_id)
        events = [event.to_dict() for event in self.history(action_id)]
        payload = {
            "schema_version": SCHEMA_VERSION,
            "action": action.to_dict(),
            "events": events,
        }
        return {**payload, "bundle_digest": _sha256(payload)}

    def _import_legacy_consumed(self, action_id: str) -> None:
        at = "1970-01-01T00:00:00+00:00"
        action_digest = _sha256(
            {"schema": "valta.legacy-seen-action.v1", "action_id": action_id}
        )
        with self._transaction() as conn:
            if conn.execute(
                "SELECT 1 FROM actions WHERE action_id = ?", (action_id,)
            ).fetchone():
                return
            decision = {
                "verdict": "ALLOW",
                "reason_code": "LEGACY_CONSUMED",
                "evidence_ref": action_digest,
            }
            conn.execute(
                """
                INSERT INTO actions (
                    action_id, action_digest, state, version, generation,
                    policy_version, decision_json, reservation_expires_at,
                    dispatch_status, final_verdict, updated_at, last_event_digest
                ) VALUES (?, ?, ?, 1, 1, 'legacy', ?, NULL, 'LEGACY',
                          'VERIFIED', ?, '')
                """,
                (
                    action_id,
                    action_digest,
                    ActionState.FINALIZED.value,
                    _canonical_json(decision),
                    at,
                ),
            )
            self._append_event(
                conn,
                action_id=action_id,
                event_type="LEGACY_ACTION_IMPORTED",
                from_state=None,
                to_state=ActionState.FINALIZED.value,
                version=1,
                generation=1,
                at=at,
                evidence=decision,
            )


class ActionLedger(SQLiteActionStore):
    """Backward-compatible name for the durable lifecycle store.

    It is no longer a boolean seen-ID set. `verify_action` records only an
    evaluation. The action identity becomes owned by an execution attempt only
    after `reserve_if_version_matches` succeeds.
    """

    def __init__(
        self,
        seen_action_ids: Iterable[str] | None = None,
        *,
        db_path: str | Path = ":memory:",
    ) -> None:
        super().__init__(db_path=db_path)
        for action_id in seen_action_ids or ():
            self._import_legacy_consumed(action_id)

    def contains(self, action_id: str) -> bool:
        record = self.get_optional(action_id)
        return record is not None and record.state in _ACTIVE_OR_CONSUMED_STATES

    def record(self, action_id: str) -> None:
        """Import a legacy consumed identity; new code must use lifecycle methods."""

        self._import_legacy_consumed(action_id)


def verify_receipt_bundle(bundle: dict[str, Any]) -> bool:
    """Verify hash-chain integrity and the final action snapshot."""

    try:
        if bundle["schema_version"] != SCHEMA_VERSION:
            return False
        action = bundle["action"]
        events = bundle["events"]
        expected_bundle_digest = bundle["bundle_digest"]
        payload = {
            "schema_version": bundle["schema_version"],
            "action": action,
            "events": events,
        }
        if _sha256(payload) != expected_bundle_digest:
            return False
        if not events:
            return False

        previous_digest: str | None = None
        for index, event in enumerate(events, start=1):
            if event["sequence"] != index:
                return False
            if event["previous_digest"] != previous_digest:
                return False
            event_payload = {
                "action_id": event["action_id"],
                "sequence": event["sequence"],
                "event_type": event["event_type"],
                "from_state": event["from_state"],
                "to_state": event["to_state"],
                "version": event["version"],
                "generation": event["generation"],
                "at": event["at"],
                "evidence": event["evidence"],
                "previous_digest": event["previous_digest"],
            }
            if _sha256(event_payload) != event["event_digest"]:
                return False
            previous_digest = event["event_digest"]

        last = events[-1]
        return (
            action["action_id"] == last["action_id"]
            and action["state"] == last["to_state"]
            and action["version"] == last["version"]
            and action["generation"] == last["generation"]
            and action["last_event_digest"] == last["event_digest"]
        )
    except (KeyError, TypeError, ValueError):
        return False
