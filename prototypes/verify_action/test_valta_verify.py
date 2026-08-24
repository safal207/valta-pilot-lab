from decimal import Decimal
import unittest

from valta_verify import (
    ALLOW,
    BLOCK,
    ActionLedger,
    ActionRequest,
    Policy,
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

    def test_normal_allowed_action(self):
        decision = verify_action(self.request(), self.policy, self.ledger)
        self.assertEqual(decision.verdict, ALLOW)
        self.assertEqual(decision.reason_code, "POLICY_SATISFIED")
        self.assertTrue(decision.evidence_ref.startswith("sha256:"))

    def test_policy_violating_action_is_blocked(self):
        decision = verify_action(
            self.request(amount=Decimal("150.00")), self.policy, self.ledger
        )
        self.assertEqual(decision.verdict, BLOCK)
        self.assertEqual(decision.reason_code, "AMOUNT_EXCEEDS_POLICY")

    def test_retry_duplicate_is_detected(self):
        first = verify_action(self.request(), self.policy, self.ledger)
        second = verify_action(self.request(), self.policy, self.ledger)
        self.assertEqual(first.verdict, ALLOW)
        self.assertEqual(second.verdict, BLOCK)
        self.assertEqual(second.reason_code, "DUPLICATE_ACTION_ID")

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

    def test_decision_does_not_claim_external_execution(self):
        decision = verify_action(self.request(), self.policy, self.ledger)
        self.assertEqual(decision.verdict, ALLOW)
        self.assertEqual(decision.execution_boundary, "EXTERNAL_UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
