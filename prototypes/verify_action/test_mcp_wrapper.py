from __future__ import annotations

import unittest

from mcp import Client

from mcp_server import evaluate_mcp_request, mcp
from valta_verify import ActionLedger


BASE_ARGS = {
    "actor": "agent-1",
    "action": "pay",
    "target": "vendor-a",
    "amount": "25.00",
    "action_id": "mcp-act-001",
    "policy_version": "policy-v1",
    "checked_at": "2026-08-24T09:00:00+00:00",
    "allowed_actions": ["pay"],
    "allowed_targets": ["vendor-a"],
    "max_amount": "100.00",
    "authorization_expires_at": "2026-08-24T10:00:00+00:00",
    "execution_observed": False,
}


class MCPWrapperTests(unittest.TestCase):
    def test_direct_wrapper_preserves_allow_semantics(self):
        decision = evaluate_mcp_request(**BASE_ARGS, ledger=ActionLedger())
        self.assertEqual(decision["verdict"], "ALLOW")
        self.assertEqual(decision["reason_code"], "POLICY_SATISFIED")
        self.assertEqual(decision["execution_boundary"], "EXTERNAL_UNVERIFIED")
        self.assertTrue(decision["action_digest"].startswith("sha256:"))
        self.assertTrue(decision["evidence_ref"].startswith("sha256:"))

    def test_direct_wrapper_preserves_policy_block(self):
        args = {**BASE_ARGS, "amount": "150.00", "action_id": "mcp-act-block"}
        decision = evaluate_mcp_request(**args, ledger=ActionLedger())
        self.assertEqual(decision["verdict"], "BLOCK")
        self.assertEqual(decision["reason_code"], "AMOUNT_EXCEEDS_POLICY")

    def test_direct_wrapper_preserves_stale_authorization(self):
        args = {
            **BASE_ARGS,
            "action_id": "mcp-act-stale",
            "checked_at": "2026-08-24T11:00:00+00:00",
        }
        decision = evaluate_mcp_request(**args, ledger=ActionLedger())
        self.assertEqual(decision["verdict"], "BLOCK")
        self.assertEqual(decision["reason_code"], "STALE_AUTHORIZATION")

    def test_explicitly_consumed_identity_is_still_blocked(self):
        args = {**BASE_ARGS, "action_id": "mcp-act-consumed"}
        decision = evaluate_mcp_request(
            **args,
            ledger=ActionLedger({"mcp-act-consumed"}),
        )
        self.assertEqual(decision["verdict"], "BLOCK")
        self.assertEqual(decision["reason_code"], "DUPLICATE_ACTION_ID")


class MCPRoundTripTests(unittest.IsolatedAsyncioTestCase):
    async def test_in_memory_mcp_round_trip_returns_structured_verdict(self):
        args = {**BASE_ARGS, "action_id": "mcp-roundtrip-allow"}
        async with Client(mcp, raise_exceptions=True) as client:
            tools = await client.list_tools()
            self.assertIn("verify_action", {tool.name for tool in tools.tools})

            result = await client.call_tool("verify_action", args)

        self.assertFalse(result.is_error)
        self.assertIsNotNone(result.structured_content)
        self.assertEqual(result.structured_content["verdict"], "ALLOW")
        self.assertEqual(
            result.structured_content["execution_boundary"], "EXTERNAL_UNVERIFIED"
        )
        self.assertTrue(result.structured_content["action_digest"].startswith("sha256:"))
        self.assertTrue(result.structured_content["evidence_ref"].startswith("sha256:"))

    async def test_repeated_mcp_evaluation_does_not_consume_action_identity(self):
        args = {**BASE_ARGS, "action_id": "mcp-roundtrip-repeat"}
        async with Client(mcp, raise_exceptions=True) as client:
            first = await client.call_tool("verify_action", args)
            second = await client.call_tool("verify_action", args)

        self.assertEqual(first.structured_content["verdict"], "ALLOW")
        self.assertEqual(second.structured_content["verdict"], "ALLOW")
        self.assertEqual(
            first.structured_content["action_digest"],
            second.structured_content["action_digest"],
        )


if __name__ == "__main__":
    unittest.main()
