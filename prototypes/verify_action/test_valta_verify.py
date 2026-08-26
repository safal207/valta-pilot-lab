from decimal import Decimal
import unittest

from valta_verify import (
    ALLOW,
    BLOCK,
    ActionLedger,
    ActionRequest,
    Policy,
    canonical_action_digest,
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
        request = self.request()
        decision = verify_action(request, self.policy, self.ledger)
        self.assertEqual(decision.verdict, ALLOW)
        self.assertEqual(decision.reason_code, "POLICY_SATISFIED")
        self.assertEqual(decision.action_digest, canonical_action_digest(request))
        self.assertTrue(decision.evidence_ref.startswith("sha256:"))

    def test_policy_violating_action_is_blocked(self):
        decision = verify_action(
            self.request(amount=Decimal("150.00")), self.policy, self.ledger
        )
        self.assertEqual(decision.verdict, BLOCK)
        self.assertEqual(decision.reason_code, "AMOUNT_EXCEEDS_POLICY")

    def test_allow_does_not_consume_action_identity(self):
        first = verify_action(self.request(), self.policy, self.ledger)
        second = verify_action(self.request(), self.policy, self.ledger)
        self.assertEqual(first.verdict, ALLOW)
        self.assertEqual(second.verdict, ALLOW)
        self.assertFalse(self.ledger.contains("act-001"))

    def test_explicitly_consumed_identity_is_detected(self):
        self.ledger.record("act-001")
        decision = verify_action(self.request(), self.policy, self.ledger)
        self.assertEqual(decision.verdict, BLOCK)
        self.assertEqual(decision.reason_code, "DUPLICATE_ACTION_ID")

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

    def test_checked_at_changes_evidence_not_action_identity(self):
        first = self.request(checked_at="2026-08-24T09:00:00+00:00")
        second = self.request(checked_at="2026-08-24T09:30:00+00:00")
        self.assertEqual(canonical_action_digest(first), canonical_action_digest(second))
        first_decision = verify_action(first, self.policy, self.ledger)
        second_decision = verify_action(second, self.policy, self.ledger)
        self.assertNotEqual(first_decision.evidence_ref, second_decision.evidence_ref)


if __name__ == "__main__":
    unittest.main()
