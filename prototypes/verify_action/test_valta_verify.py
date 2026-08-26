from decimal import Decimal
import unittest

from action_lifecycle import ActionState
from valta_verify import (
    ALLOW,
    BLOCK,
    INCONCLUSIVE,
    ActionLedger,
    ActionRequest,
    Policy,
    action_digest,
    verify_action,
)


class VerifyActionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = Policy(
            version="policy-v1",
            allowed_actions=frozenset({"pay"}),
            allowed_targets=frozenset({"vendor-a"}),
            max_amount=Decimal("100.00"),
        )
        self.ledger = ActionLedger()

    def tearDown(self) -> None:
        self.ledger.close()

    def request(self, **overrides):
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

    def test_normal_allowed_action_is_evaluated_not_consumed(self):
        request = self.request()
        decision = verify_action(request, self.policy, self.ledger)
        record = self.ledger.get(request.action_id)

        self.assertEqual(decision.verdict, ALLOW)
        self.assertEqual(decision.reason_code, "POLICY_SATISFIED")
        self.assertTrue(decision.evidence_ref.startswith("sha256:"))
        self.assertEqual(record.state, ActionState.EVALUATED.value)
        self.assertFalse(self.ledger.contains(request.action_id))

    def test_repeated_evaluation_is_idempotent_and_does_not_create_duplicate(self):
        request = self.request()
        first = verify_action(request, self.policy, self.ledger)
        first_record = self.ledger.get(request.action_id)
        second = verify_action(request, self.policy, self.ledger)
        second_record = self.ledger.get(request.action_id)

        self.assertEqual(first.verdict, ALLOW)
        self.assertEqual(second.verdict, ALLOW)
        self.assertEqual(first.evidence_ref, second.evidence_ref)
        self.assertEqual(first_record.version, second_record.version)
        self.assertEqual(len(self.ledger.history(request.action_id)), 2)

    def test_policy_violating_action_is_blocked(self):
        decision = verify_action(
            self.request(amount=Decimal("150.00")), self.policy, self.ledger
        )
        self.assertEqual(decision.verdict, BLOCK)
        self.assertEqual(decision.reason_code, "AMOUNT_EXCEEDS_POLICY")
        self.assertEqual(
            self.ledger.get("act-001").state, ActionState.BLOCKED.value
        )

    def test_stale_authorization_is_rejected(self):
        decision = verify_action(
            self.request(
                checked_at="2026-08-24T11:00:00+00:00",
                authorization_expires_at="2026-08-24T10:00:00+00:00",
            ),
            self.policy,
            self.ledger,
        )
        self.assertEqual(decision.verdict, BLOCK)
        self.assertEqual(decision.reason_code, "STALE_AUTHORIZATION")

    def test_negative_amount_is_inconclusive(self):
        decision = verify_action(
            self.request(amount=Decimal("-1.00")), self.policy, self.ledger
        )
        self.assertEqual(decision.verdict, INCONCLUSIVE)
        self.assertEqual(decision.reason_code, "INVALID_NEGATIVE_AMOUNT")

    def test_action_id_cannot_be_rebound_to_different_action(self):
        first_request = self.request()
        first = verify_action(first_request, self.policy, self.ledger)
        second = verify_action(
            self.request(amount=Decimal("26.00")), self.policy, self.ledger
        )

        self.assertEqual(first.verdict, ALLOW)
        self.assertEqual(second.verdict, BLOCK)
        self.assertEqual(second.reason_code, "ACTION_ID_CONFLICT")
        self.assertEqual(
            self.ledger.get(first_request.action_id).action_digest,
            action_digest(first_request),
        )

    def test_reserved_action_is_a_duplicate_for_new_evaluation(self):
        request = self.request()
        first = verify_action(request, self.policy, self.ledger)
        self.assertEqual(first.verdict, ALLOW)
        evaluated = self.ledger.get(request.action_id)
        self.ledger.reserve_if_version_matches(
            action_id=request.action_id,
            action_digest=evaluated.action_digest,
            expected_version=evaluated.version,
            reserved_at="2026-08-24T09:01:00+00:00",
            reservation_expires_at="2026-08-24T09:05:00+00:00",
        )

        retry = verify_action(request, self.policy, self.ledger)
        self.assertEqual(retry.verdict, BLOCK)
        self.assertEqual(retry.reason_code, "DUPLICATE_ACTION_ID")

    def test_decision_does_not_claim_external_execution(self):
        decision = verify_action(self.request(), self.policy, self.ledger)
        self.assertEqual(decision.verdict, ALLOW)
        self.assertEqual(decision.execution_boundary, "EXTERNAL_UNVERIFIED")

    def test_caller_observation_is_labeled_as_asserted_not_verified_finality(self):
        decision = verify_action(
            self.request(execution_observed=True), self.policy, self.ledger
        )
        self.assertEqual(decision.execution_boundary, "CALLER_ASSERTED_EXECUTION")


if __name__ == "__main__":
    unittest.main()
