from __future__ import annotations

import copy
import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

from action_lifecycle import (
    ActionState,
    ConcurrencyConflict,
    SQLiteActionStore,
    StateConflict,
    verify_receipt_bundle,
)
from valta_verify import ActionRequest, Policy, action_digest, verify_action


class DurableActionLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        fd, self.db_path = tempfile.mkstemp(prefix="valta-actions-", suffix=".sqlite3")
        os.close(fd)
        self.store = SQLiteActionStore(self.db_path)
        self.policy = Policy(
            version="policy-v1",
            allowed_actions=frozenset({"pay"}),
            allowed_targets=frozenset({"vendor-a"}),
            max_amount=Decimal("100.00"),
        )

    def tearDown(self) -> None:
        self.store.close()
        for suffix in ("", "-wal", "-shm"):
            try:
                os.remove(self.db_path + suffix)
            except FileNotFoundError:
                pass

    def request(self, action_id: str = "act-lifecycle-001") -> ActionRequest:
        return ActionRequest(
            actor="agent-1",
            action="pay",
            target="vendor-a",
            amount=Decimal("25.00"),
            action_id=action_id,
            policy_version="policy-v1",
            checked_at="2026-08-24T09:00:00+00:00",
            authorization_expires_at="2026-08-24T10:00:00+00:00",
        )

    def evaluate(self, request: ActionRequest | None = None):
        request = request or self.request()
        decision = verify_action(request, self.policy, self.store)
        self.assertEqual(decision.verdict, "ALLOW")
        return request, self.store.get(request.action_id)

    def reserve(self, request: ActionRequest, record):
        return self.store.reserve_if_version_matches(
            action_id=request.action_id,
            action_digest=action_digest(request),
            expected_version=record.version,
            reserved_at="2026-08-24T09:01:00+00:00",
            reservation_expires_at="2026-08-24T09:05:00+00:00",
        )

    def start_dispatch(self, request: ActionRequest, record):
        return self.store.mark_dispatch_started(
            action_id=request.action_id,
            expected_version=record.version,
            generation=record.generation,
            started_at="2026-08-24T09:02:00+00:00",
            adapter="sandbox-ledger",
            downstream_idempotency_key=request.action_id,
        )

    def test_normal_reserve_dispatch_observe_finalize_and_receipt(self):
        request, evaluated = self.evaluate()
        reserved = self.reserve(request, evaluated)
        dispatching = self.start_dispatch(request, reserved)
        dispatched = self.store.record_dispatch_result(
            action_id=request.action_id,
            expected_version=dispatching.version,
            generation=dispatching.generation,
            status="ACCEPTED",
            observed_at="2026-08-24T09:02:10+00:00",
            downstream_request_id="sandbox-req-1",
        )
        observing = self.store.begin_observation(
            action_id=request.action_id,
            expected_version=dispatched.version,
            generation=dispatched.generation,
            observed_at="2026-08-24T09:02:20+00:00",
        )
        verified = self.store.record_observation(
            action_id=request.action_id,
            expected_version=observing.version,
            generation=observing.generation,
            status="MATCHED",
            observed_at="2026-08-24T09:02:30+00:00",
            evidence_ref="sandbox-ledger:entry-1",
        )
        finalized = self.store.finalize_if_version_matches(
            action_id=request.action_id,
            expected_version=verified.version,
            generation=verified.generation,
            finalized_at="2026-08-24T09:02:40+00:00",
            final_verdict="VERIFIED",
        )

        self.assertEqual(finalized.state, ActionState.FINALIZED.value)
        self.assertEqual(finalized.final_verdict, "VERIFIED")
        self.assertIsNotNone(finalized.fencing_token)
        bundle = self.store.export_receipt(request.action_id)
        self.assertTrue(verify_receipt_bundle(bundle))
        self.assertEqual(bundle, self.store.export_receipt(request.action_id))

    def test_two_concurrent_reservations_have_one_owner(self):
        request, evaluated = self.evaluate(self.request("act-concurrent"))
        peer = SQLiteActionStore(self.db_path)
        try:
            def attempt(store):
                return store.reserve_if_version_matches(
                    action_id=request.action_id,
                    action_digest=action_digest(request),
                    expected_version=evaluated.version,
                    reserved_at="2026-08-24T09:01:00+00:00",
                    reservation_expires_at="2026-08-24T09:05:00+00:00",
                )

            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(attempt, store) for store in (self.store, peer)]
                results = []
                errors = []
                for future in futures:
                    try:
                        results.append(future.result())
                    except Exception as exc:  # asserted precisely below
                        errors.append(exc)

            self.assertEqual(len(results), 1)
            self.assertEqual(len(errors), 1)
            self.assertIsInstance(errors[0], ConcurrencyConflict)
            self.assertEqual(results[0].generation, 1)
            self.assertEqual(self.store.get(request.action_id).state, ActionState.RESERVED.value)
        finally:
            peer.close()

    def test_restart_after_allow_before_reserve_does_not_consume_action(self):
        request, evaluated = self.evaluate(self.request("act-restart-evaluated"))
        self.store.close()
        self.store = SQLiteActionStore(self.db_path)

        recovered = self.store.get(request.action_id)
        self.assertEqual(recovered.state, ActionState.EVALUATED.value)
        reserved = self.reserve(request, recovered)
        self.assertEqual(reserved.state, ActionState.RESERVED.value)

    def test_restart_after_reserve_can_release_known_no_effect_and_retry(self):
        request, evaluated = self.evaluate(self.request("act-release-retry"))
        reserved = self.reserve(request, evaluated)
        self.store.close()
        self.store = SQLiteActionStore(self.db_path)

        recovered = self.store.get(request.action_id)
        released = self.store.release_if_safe(
            action_id=request.action_id,
            expected_version=recovered.version,
            generation=recovered.generation,
            released_at="2026-08-24T09:02:00+00:00",
            no_effect_evidence_ref="internal:no-dispatch-event",
        )
        self.assertEqual(released.state, ActionState.RELEASED_NO_EFFECT.value)

        decision = verify_action(request, self.policy, self.store)
        self.assertEqual(decision.verdict, "ALLOW")
        reevaluated = self.store.get(request.action_id)
        retried = self.reserve(request, reevaluated)
        self.assertEqual(retried.generation, 2)

    def test_restart_while_dispatching_requires_reconciliation(self):
        request, evaluated = self.evaluate(self.request("act-dispatch-crash"))
        reserved = self.reserve(request, evaluated)
        dispatching = self.start_dispatch(request, reserved)
        self.store.close()
        self.store = SQLiteActionStore(self.db_path)

        recovered = self.store.recover_after_restart(
            action_id=request.action_id,
            expected_version=dispatching.version,
            generation=dispatching.generation,
            recovered_at="2026-08-24T09:03:00+00:00",
        )
        self.assertEqual(recovered.state, ActionState.RECONCILE_REQUIRED.value)
        with self.assertRaises(StateConflict):
            self.store.reserve_if_version_matches(
                action_id=request.action_id,
                action_digest=action_digest(request),
                expected_version=recovered.version,
                reserved_at="2026-08-24T09:04:00+00:00",
                reservation_expires_at="2026-08-24T09:06:00+00:00",
            )

    def test_provider_accepted_but_final_state_absent_is_unverified(self):
        request, evaluated = self.evaluate(self.request("act-false-success"))
        reserved = self.reserve(request, evaluated)
        dispatching = self.start_dispatch(request, reserved)
        dispatched = self.store.record_dispatch_result(
            action_id=request.action_id,
            expected_version=dispatching.version,
            generation=dispatching.generation,
            status="ACCEPTED",
            observed_at="2026-08-24T09:02:10+00:00",
        )
        observing = self.store.begin_observation(
            action_id=request.action_id,
            expected_version=dispatched.version,
            generation=dispatched.generation,
            observed_at="2026-08-24T09:02:20+00:00",
        )
        unverified = self.store.record_observation(
            action_id=request.action_id,
            expected_version=observing.version,
            generation=observing.generation,
            status="ABSENT",
            observed_at="2026-08-24T09:02:30+00:00",
            evidence_ref="sandbox-ledger:no-entry-after-finality-window",
        )
        self.assertEqual(unverified.state, ActionState.UNVERIFIED.value)
        finalized = self.store.finalize_if_version_matches(
            action_id=request.action_id,
            expected_version=unverified.version,
            generation=unverified.generation,
            finalized_at="2026-08-24T09:02:40+00:00",
            final_verdict="UNVERIFIED",
        )
        self.assertEqual(finalized.final_verdict, "UNVERIFIED")

    def test_timeout_after_dispatch_is_not_treated_as_no_effect(self):
        request, evaluated = self.evaluate(self.request("act-timeout"))
        reserved = self.reserve(request, evaluated)
        dispatching = self.start_dispatch(request, reserved)
        uncertain = self.store.record_dispatch_result(
            action_id=request.action_id,
            expected_version=dispatching.version,
            generation=dispatching.generation,
            status="UNKNOWN",
            observed_at="2026-08-24T09:02:10+00:00",
        )

        self.assertEqual(uncertain.state, ActionState.RECONCILE_REQUIRED.value)
        with self.assertRaises(StateConflict):
            self.store.release_if_safe(
                action_id=request.action_id,
                expected_version=uncertain.version,
                generation=uncertain.generation,
                released_at="2026-08-24T09:03:00+00:00",
                no_effect_evidence_ref="timeout-is-not-proof",
            )

    def test_expired_pre_dispatch_reservation_can_be_released(self):
        request, evaluated = self.evaluate(self.request("act-expired"))
        reserved = self.reserve(request, evaluated)
        expired = self.store.expire_reservation(
            action_id=request.action_id,
            expected_version=reserved.version,
            generation=reserved.generation,
            checked_at="2026-08-24T09:05:00+00:00",
        )
        released = self.store.release_if_safe(
            action_id=request.action_id,
            expected_version=expired.version,
            generation=expired.generation,
            released_at="2026-08-24T09:05:01+00:00",
            no_effect_evidence_ref="state-machine:no-dispatch-started",
        )
        self.assertEqual(released.state, ActionState.RELEASED_NO_EFFECT.value)

    def test_stale_generation_cannot_write_after_safe_retry(self):
        request, evaluated = self.evaluate(self.request("act-stale-fence"))
        first = self.reserve(request, evaluated)
        released = self.store.release_if_safe(
            action_id=request.action_id,
            expected_version=first.version,
            generation=first.generation,
            released_at="2026-08-24T09:01:30+00:00",
            no_effect_evidence_ref="internal:no-dispatch-event",
        )
        self.assertEqual(verify_action(request, self.policy, self.store).verdict, "ALLOW")
        second_evaluation = self.store.get(request.action_id)
        second = self.reserve(request, second_evaluation)
        self.assertEqual(second.generation, first.generation + 1)

        with self.assertRaises(ConcurrencyConflict):
            self.store.mark_dispatch_started(
                action_id=request.action_id,
                expected_version=first.version,
                generation=first.generation,
                started_at="2026-08-24T09:02:00+00:00",
                adapter="sandbox-ledger",
                downstream_idempotency_key=request.action_id,
            )

    def test_finalized_action_cannot_create_second_effect(self):
        request, evaluated = self.evaluate(self.request("act-one-final"))
        reserved = self.reserve(request, evaluated)
        dispatching = self.start_dispatch(request, reserved)
        dispatched = self.store.record_dispatch_result(
            action_id=request.action_id,
            expected_version=dispatching.version,
            generation=dispatching.generation,
            status="ACCEPTED",
            observed_at="2026-08-24T09:02:10+00:00",
        )
        verified = self.store.record_observation(
            action_id=request.action_id,
            expected_version=dispatched.version,
            generation=dispatched.generation,
            status="MATCHED",
            observed_at="2026-08-24T09:02:20+00:00",
            evidence_ref="sandbox-ledger:entry-final",
        )
        finalized = self.store.finalize_if_version_matches(
            action_id=request.action_id,
            expected_version=verified.version,
            generation=verified.generation,
            finalized_at="2026-08-24T09:02:30+00:00",
            final_verdict="VERIFIED",
        )

        retry_decision = verify_action(request, self.policy, self.store)
        self.assertEqual(retry_decision.verdict, "BLOCK")
        self.assertEqual(retry_decision.reason_code, "DUPLICATE_ACTION_ID")
        with self.assertRaises(StateConflict):
            self.store.reserve_if_version_matches(
                action_id=request.action_id,
                action_digest=action_digest(request),
                expected_version=finalized.version,
                reserved_at="2026-08-24T09:03:00+00:00",
                reservation_expires_at="2026-08-24T09:04:00+00:00",
            )

    def test_receipt_tampering_is_detected(self):
        request, evaluated = self.evaluate(self.request("act-tamper"))
        self.reserve(request, evaluated)
        bundle = self.store.export_receipt(request.action_id)
        tampered = copy.deepcopy(bundle)
        tampered["events"][-1]["evidence"]["reservation_expires_at"] = (
            "2030-01-01T00:00:00+00:00"
        )
        self.assertFalse(verify_receipt_bundle(tampered))


if __name__ == "__main__":
    unittest.main()
