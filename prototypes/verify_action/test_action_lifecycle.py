from __future__ import annotations

import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path

from action_lifecycle import (
    DISPATCH_ACCEPTED,
    DISPATCH_UNKNOWN,
    EVALUATED,
    FINALIZED,
    OBSERVED_EXPECTED_EFFECT,
    OBSERVED_NO_EFFECT,
    RECONCILE_REQUIRED,
    RELEASED_NO_EFFECT,
    RESERVED,
    UNVERIFIED,
    VERIFIED,
    ActionDigestMismatchError,
    ActionLifecycle,
    EvidenceIntegrityError,
    SQLiteActionStore,
    StaleGenerationError,
    StaleVersionError,
    StateConflictError,
    UnsafeReleaseError,
    verify_receipt,
)
from valta_verify import ActionRequest, Policy, verify_action


class ActionLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tempdir.name) / "actions.sqlite3"
        self.store = SQLiteActionStore(self.db_path)
        self.lifecycle = ActionLifecycle(self.store)
        self.policy = Policy(
            version="policy-v1",
            allowed_actions=frozenset({"pay"}),
            allowed_targets=frozenset({"vendor-a"}),
            max_amount=Decimal("100.00"),
        )

    def tearDown(self) -> None:
        self.store.close()
        self.tempdir.cleanup()

    def request(self, **overrides) -> ActionRequest:
        data = {
            "actor": "agent-1",
            "action": "pay",
            "target": "vendor-a",
            "amount": Decimal("25.00"),
            "action_id": "act-001",
            "policy_version": "policy-v1",
            "checked_at": "2026-08-24T09:00:00+00:00",
            "authorization_expires_at": "2026-08-24T10:00:00+00:00",
            "execution_observed": False,
        }
        data.update(overrides)
        return ActionRequest(**data)

    def evaluate(self, **overrides):
        return self.lifecycle.evaluate(self.request(**overrides), self.policy)

    def reserve(self, record, *, evidence_at="2026-08-24T09:01:00+00:00"):
        return self.store.reserve(
            record.action_id,
            expected_version=record.version,
            evidence_at=evidence_at,
            evidence={"owner": "worker-a"},
        )

    def dispatch(self, record):
        dispatching = self.store.mark_dispatching(
            record.action_id,
            expected_version=record.version,
            generation=record.generation,
            evidence_at="2026-08-24T09:02:00+00:00",
            adapter="sandbox-ledger-v1",
            downstream_idempotency_key=record.action_id,
        )
        return self.store.record_dispatch_result(
            record.action_id,
            expected_version=dispatching.version,
            generation=dispatching.generation,
            evidence_at="2026-08-24T09:03:00+00:00",
            status=DISPATCH_ACCEPTED,
            downstream_request_id="sandbox-req-1",
        )

    def test_normal_reserve_dispatch_observe_finalize(self):
        decision, evaluated = self.evaluate()
        self.assertEqual(decision.verdict, "ALLOW")
        self.assertEqual(evaluated.state, EVALUATED)

        reserved = self.reserve(evaluated)
        dispatched = self.dispatch(reserved)
        observing = self.store.begin_observation(
            dispatched.action_id,
            expected_version=dispatched.version,
            generation=dispatched.generation,
            evidence_at="2026-08-24T09:04:00+00:00",
            evidence_source="sandbox-ledger",
        )
        verified = self.store.record_observation(
            observing.action_id,
            expected_version=observing.version,
            generation=observing.generation,
            evidence_at="2026-08-24T09:05:00+00:00",
            status=OBSERVED_EXPECTED_EFFECT,
            evidence_source="sandbox-ledger",
            evidence={"settled_amount": "25.00", "recipient": "vendor-a"},
        )
        finalized = self.store.finalize(
            verified.action_id,
            expected_version=verified.version,
            generation=verified.generation,
            evidence_at="2026-08-24T09:06:00+00:00",
            final_verdict=VERIFIED,
        )

        self.assertEqual(finalized.state, FINALIZED)
        self.assertEqual(finalized.final_verdict, VERIFIED)
        self.assertTrue(self.store.verify_history(finalized.action_id))
        receipt = self.store.export_receipt(finalized.action_id)
        self.assertEqual(receipt["action"]["state"], FINALIZED)
        self.assertEqual(len(receipt["events"]), 7)
        self.assertTrue(verify_receipt(receipt))

    def test_two_concurrent_reservations_have_one_owner(self):
        _, evaluated = self.evaluate()

        def attempt(owner: str):
            try:
                record = self.store.reserve(
                    evaluated.action_id,
                    expected_version=evaluated.version,
                    evidence_at="2026-08-24T09:01:00+00:00",
                    evidence={"owner": owner},
                )
                return ("reserved", record.generation)
            except (StaleVersionError, StateConflictError) as exc:
                return ("rejected", type(exc).__name__)

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(attempt, ["worker-a", "worker-b"]))

        self.assertEqual(sum(result[0] == "reserved" for result in results), 1)
        self.assertEqual(sum(result[0] == "rejected" for result in results), 1)
        self.assertEqual(self.store.get_action(evaluated.action_id).state, RESERVED)

    def test_crash_after_allow_before_reserve_recovers(self):
        _, evaluated = self.evaluate()
        self.store.close()
        self.store = SQLiteActionStore(self.db_path)
        self.lifecycle = ActionLifecycle(self.store)

        recovered = self.store.get_action(evaluated.action_id)
        self.assertEqual(recovered.state, EVALUATED)
        reserved = self.reserve(recovered)
        self.assertEqual(reserved.state, RESERVED)

    def test_crash_after_reserve_before_dispatch_recovers_same_generation(self):
        _, evaluated = self.evaluate()
        reserved = self.reserve(evaluated)
        generation = reserved.generation
        self.store.close()
        self.store = SQLiteActionStore(self.db_path)
        self.lifecycle = ActionLifecycle(self.store)

        recovered = self.store.get_action(reserved.action_id)
        dispatching = self.store.mark_dispatching(
            recovered.action_id,
            expected_version=recovered.version,
            generation=generation,
            evidence_at="2026-08-24T09:02:00+00:00",
            adapter="sandbox-ledger-v1",
            downstream_idempotency_key=recovered.action_id,
        )
        self.assertEqual(dispatching.generation, generation)

    def test_provider_acceptance_without_effect_is_unverified(self):
        _, evaluated = self.evaluate()
        dispatched = self.dispatch(self.reserve(evaluated))
        observing = self.store.begin_observation(
            dispatched.action_id,
            expected_version=dispatched.version,
            generation=dispatched.generation,
            evidence_at="2026-08-24T09:04:00+00:00",
            evidence_source="sandbox-ledger",
        )
        unverified = self.store.record_observation(
            observing.action_id,
            expected_version=observing.version,
            generation=observing.generation,
            evidence_at="2026-08-24T09:05:00+00:00",
            status=OBSERVED_NO_EFFECT,
            evidence_source="sandbox-ledger",
            evidence={"settled_amount": "0.00"},
        )
        self.assertEqual(unverified.state, UNVERIFIED)
        finalized = self.store.finalize(
            unverified.action_id,
            expected_version=unverified.version,
            generation=unverified.generation,
            evidence_at="2026-08-24T09:06:00+00:00",
            final_verdict=UNVERIFIED,
        )
        self.assertEqual(finalized.final_verdict, UNVERIFIED)

    def test_timeout_after_dispatch_requires_reconciliation(self):
        _, evaluated = self.evaluate()
        reserved = self.reserve(evaluated)
        dispatching = self.store.mark_dispatching(
            reserved.action_id,
            expected_version=reserved.version,
            generation=reserved.generation,
            evidence_at="2026-08-24T09:02:00+00:00",
            adapter="sandbox-ledger-v1",
            downstream_idempotency_key=reserved.action_id,
        )
        unknown = self.store.record_dispatch_result(
            dispatching.action_id,
            expected_version=dispatching.version,
            generation=dispatching.generation,
            evidence_at="2026-08-24T09:03:00+00:00",
            status=DISPATCH_UNKNOWN,
            evidence={"transport": "timeout"},
        )
        self.assertEqual(unknown.state, RECONCILE_REQUIRED)
        with self.assertRaises(StateConflictError):
            self.store.reserve(
                unknown.action_id,
                expected_version=unknown.version,
                evidence_at="2026-08-24T09:04:00+00:00",
            )

    def test_known_no_effect_release_allows_new_generation_after_reevaluation(self):
        request = self.request()
        decision, evaluated = self.lifecycle.evaluate(request, self.policy)
        reserved = self.reserve(evaluated)
        released = self.store.release_no_effect(
            reserved.action_id,
            expected_version=reserved.version,
            generation=reserved.generation,
            evidence_at="2026-08-24T09:02:00+00:00",
            known_no_effect=True,
            evidence={"dispatch_started": False, "adapter_check": "no request recorded"},
        )
        self.assertEqual(released.state, RELEASED_NO_EFFECT)

        fresh_request = self.request(checked_at="2026-08-24T09:10:00+00:00")
        fresh_decision = verify_action(fresh_request, self.policy, self.store)
        reevaluated = self.store.record_evaluation(fresh_request, fresh_decision)
        second = self.store.reserve(
            reevaluated.action_id,
            expected_version=reevaluated.version,
            evidence_at="2026-08-24T09:11:00+00:00",
        )
        self.assertEqual(second.generation, reserved.generation + 1)
        self.assertEqual(decision.action_digest, fresh_decision.action_digest)

    def test_release_without_known_no_effect_is_rejected(self):
        _, evaluated = self.evaluate()
        reserved = self.reserve(evaluated)
        with self.assertRaises(UnsafeReleaseError):
            self.store.release_no_effect(
                reserved.action_id,
                expected_version=reserved.version,
                generation=reserved.generation,
                evidence_at="2026-08-24T09:02:00+00:00",
                known_no_effect=False,
                evidence={},
            )

    def test_stale_generation_cannot_dispatch_after_new_reservation(self):
        request = self.request()
        _, evaluated = self.lifecycle.evaluate(request, self.policy)
        first = self.reserve(evaluated)
        released = self.store.release_no_effect(
            first.action_id,
            expected_version=first.version,
            generation=first.generation,
            evidence_at="2026-08-24T09:02:00+00:00",
            known_no_effect=True,
            evidence={"dispatch_started": False},
        )
        fresh_request = self.request(checked_at="2026-08-24T09:10:00+00:00")
        fresh_decision = verify_action(fresh_request, self.policy, self.store)
        reevaluated = self.store.record_evaluation(fresh_request, fresh_decision)
        second = self.store.reserve(
            reevaluated.action_id,
            expected_version=reevaluated.version,
            evidence_at="2026-08-24T09:11:00+00:00",
        )

        with self.assertRaises(StaleGenerationError):
            self.store.mark_dispatching(
                second.action_id,
                expected_version=second.version,
                generation=first.generation,
                evidence_at="2026-08-24T09:12:00+00:00",
                adapter="sandbox-ledger-v1",
            )
        self.assertEqual(released.generation, first.generation)

    def test_same_action_id_cannot_be_rebound_to_changed_amount(self):
        _, evaluated = self.evaluate()
        changed = self.request(amount=Decimal("30.00"))
        changed_decision = verify_action(changed, self.policy, self.store)
        self.assertEqual(changed_decision.reason_code, "ACTION_DIGEST_MISMATCH")
        with self.assertRaises(ActionDigestMismatchError):
            self.store.record_evaluation(changed, changed_decision)
        self.assertEqual(
            self.store.get_action(evaluated.action_id).action_digest,
            evaluated.action_digest,
        )

    def test_repeated_identical_evaluation_is_idempotent(self):
        request = self.request()
        decision, first = self.lifecycle.evaluate(request, self.policy)
        second = self.store.record_evaluation(request, decision)
        self.assertEqual(first.version, second.version)
        self.assertEqual(len(self.store.history(request.action_id)), 1)

    def test_finalized_action_cannot_produce_second_reservation(self):
        _, evaluated = self.evaluate()
        dispatched = self.dispatch(self.reserve(evaluated))
        observing = self.store.begin_observation(
            dispatched.action_id,
            expected_version=dispatched.version,
            generation=dispatched.generation,
            evidence_at="2026-08-24T09:04:00+00:00",
            evidence_source="sandbox-ledger",
        )
        verified = self.store.record_observation(
            observing.action_id,
            expected_version=observing.version,
            generation=observing.generation,
            evidence_at="2026-08-24T09:05:00+00:00",
            status=OBSERVED_EXPECTED_EFFECT,
            evidence_source="sandbox-ledger",
            evidence={"settled_amount": "25.00"},
        )
        final = self.store.finalize(
            verified.action_id,
            expected_version=verified.version,
            generation=verified.generation,
            evidence_at="2026-08-24T09:06:00+00:00",
            final_verdict=VERIFIED,
        )
        duplicate_decision, existing = self.lifecycle.evaluate(self.request(), self.policy)
        self.assertEqual(duplicate_decision.reason_code, "DUPLICATE_ACTION_ID")
        self.assertEqual(existing.state, FINALIZED)
        with self.assertRaises(StateConflictError):
            self.store.reserve(
                final.action_id,
                expected_version=final.version,
                evidence_at="2026-08-24T09:07:00+00:00",
            )

    def test_exported_receipt_tampering_is_detected_without_database(self):
        _, evaluated = self.evaluate()
        receipt = self.store.export_receipt(evaluated.action_id)
        receipt["action"]["state"] = "FINALIZED"
        with self.assertRaises(EvidenceIntegrityError):
            verify_receipt(receipt)

    def test_tampered_event_evidence_is_detected(self):
        _, evaluated = self.evaluate()
        self.assertTrue(self.store.verify_history(evaluated.action_id))
        connection = sqlite3.connect(self.db_path)
        try:
            connection.execute(
                "UPDATE action_events SET evidence_json = ? WHERE action_id = ? AND sequence = 1",
                ('{"tampered":true}', evaluated.action_id),
            )
            connection.commit()
        finally:
            connection.close()
        with self.assertRaises(EvidenceIntegrityError):
            self.store.verify_history(evaluated.action_id)


if __name__ == "__main__":
    unittest.main()
