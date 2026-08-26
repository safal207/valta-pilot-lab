from __future__ import annotations

import copy
import unittest

from action_lifecycle import verify_receipt_bundle
from cross_system_proof import (
    DispatchMode,
    ProofVerdict,
    SandboxAccountingLedger,
    SandboxPaymentProvider,
    SandboxRail,
    StaleFenceError,
    payout_request,
    run_named_scenario,
    run_scenario,
)


class CrossSystemProofTests(unittest.TestCase):
    def test_verified(self):
        result = run_named_scenario("verified")
        self.assertEqual(result.verdict, ProofVerdict.VERIFIED.value)
        self.assertEqual((result.rail_effects, result.ledger_effects), (1, 1))
        self.assertTrue(result.receipt_verified)

    def test_safe_to_retry(self):
        result = run_named_scenario("safe-to-retry")
        self.assertEqual(result.verdict, ProofVerdict.SAFE_TO_RETRY.value)
        self.assertEqual(result.economic_effects, 0)

    def test_accepted_without_effect(self):
        result = run_named_scenario("unverified")
        self.assertEqual(result.verdict, ProofVerdict.UNVERIFIED.value)
        self.assertEqual((result.rail_effects, result.ledger_effects), (0, 0))

    def test_timeout_after_rail_credit(self):
        result = run_named_scenario("reconcile-required")
        self.assertEqual(result.verdict, ProofVerdict.RECONCILE_REQUIRED.value)
        self.assertEqual((result.rail_effects, result.ledger_effects), (1, 0))

    def test_24_attempts_have_one_owner_and_one_effect(self):
        result = run_named_scenario("concurrent-retry")
        self.assertEqual(result.reservation_winners, 1)
        self.assertEqual(result.rejected_attempts, 23)
        self.assertEqual(result.economic_effects, 1)
        self.assertEqual(result.verdict, ProofVerdict.VERIFIED.value)

    def test_provider_replays_same_generation_idempotently(self):
        rail = SandboxRail()
        ledger = SandboxAccountingLedger()
        provider = SandboxPaymentProvider(rail=rail, ledger=ledger)
        request = payout_request("same-generation")

        first = provider.dispatch(
            request=request,
            generation=1,
            fencing_token="fence-1",
            mode=DispatchMode.SETTLED_AND_RECONCILED,
        )
        second = provider.dispatch(
            request=request,
            generation=1,
            fencing_token="fence-1",
            mode=DispatchMode.SETTLED_AND_RECONCILED,
        )

        self.assertEqual(first, second)
        self.assertEqual(len(rail.credits_for(request.action_id)), 1)

    def test_stale_generation_is_rejected_at_provider_boundary(self):
        rail = SandboxRail()
        ledger = SandboxAccountingLedger()
        provider = SandboxPaymentProvider(rail=rail, ledger=ledger)
        request = payout_request("stale-generation")

        provider.dispatch(
            request=request,
            generation=2,
            fencing_token="fence-2",
            mode=DispatchMode.REJECTED_NO_EFFECT,
        )
        with self.assertRaises(StaleFenceError):
            provider.dispatch(
                request=request,
                generation=1,
                fencing_token="fence-1",
                mode=DispatchMode.SETTLED_AND_RECONCILED,
            )

    def test_receipt_digest_is_exported(self):
        result = run_scenario(
            DispatchMode.SETTLED_AND_RECONCILED,
            action_id="receipt",
        )
        self.assertTrue(result.receipt_digest.startswith("sha256:"))
        self.assertIn("events", result.receipt_bundle)

    def test_receipt_tampering_is_detected(self):
        result = run_named_scenario("verified")
        tampered = copy.deepcopy(result.receipt_bundle)
        tampered["action"]["state"] = "RECONCILE_REQUIRED"
        self.assertFalse(verify_receipt_bundle(tampered))


if __name__ == "__main__":
    unittest.main()
