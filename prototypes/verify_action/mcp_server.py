from __future__ import annotations

import os
from decimal import Decimal

from mcp.server import MCPServer

from valta_verify import ActionLedger, ActionRequest, Policy, verify_action as verify_core


mcp = MCPServer("Valta Pilot Lab")
_server_ledger = ActionLedger(db_path=os.getenv("VALTA_ACTION_DB", ":memory:"))


def evaluate_mcp_request(
    *,
    actor: str,
    action: str,
    target: str,
    amount: str,
    action_id: str,
    policy_version: str,
    checked_at: str,
    allowed_actions: list[str],
    allowed_targets: list[str],
    max_amount: str,
    authorization_expires_at: str | None = None,
    execution_observed: bool = False,
    ledger: ActionLedger | None = None,
) -> dict[str, str]:
    """Adapt one MCP-shaped request to the deterministic core verifier.

    Policy data is explicit in the prototype so a recorded tool call contains the
    policy snapshot needed to reproduce its decision. Production code should
    resolve an authenticated policy snapshot from durable state instead.

    This wrapper evaluates only. An ALLOW verdict must still be durably reserved
    through the lifecycle API before any external dispatch.
    """

    active_ledger = ledger if ledger is not None else _server_ledger
    policy = Policy(
        version=policy_version,
        allowed_actions=frozenset(allowed_actions),
        allowed_targets=frozenset(allowed_targets),
        max_amount=Decimal(max_amount),
    )
    request = ActionRequest(
        actor=actor,
        action=action,
        target=target,
        amount=Decimal(amount),
        action_id=action_id,
        policy_version=policy_version,
        checked_at=checked_at,
        authorization_expires_at=authorization_expires_at,
        execution_observed=execution_observed,
    )
    return verify_core(request, policy, active_ledger).to_dict()


@mcp.tool()
def verify_action(
    actor: str,
    action: str,
    target: str,
    amount: str,
    action_id: str,
    policy_version: str,
    checked_at: str,
    allowed_actions: list[str],
    allowed_targets: list[str],
    max_amount: str,
    authorization_expires_at: str | None = None,
    execution_observed: bool = False,
) -> dict[str, str]:
    """Evaluate a proposed financial action and return a reproducible verdict.

    `amount` and `max_amount` are decimal strings to avoid binary floating-point
    ambiguity. This tool proves the policy decision only; it does not reserve,
    dispatch, observe, reconcile, or finalize an external effect.
    """

    return evaluate_mcp_request(
        actor=actor,
        action=action,
        target=target,
        amount=amount,
        action_id=action_id,
        policy_version=policy_version,
        checked_at=checked_at,
        allowed_actions=allowed_actions,
        allowed_targets=allowed_targets,
        max_amount=max_amount,
        authorization_expires_at=authorization_expires_at,
        execution_observed=execution_observed,
    )


def main() -> None:
    """Run the prototype over stateless Streamable HTTP with JSON responses."""

    mcp.run(transport="streamable-http", stateless_http=True, json_response=True)


if __name__ == "__main__":
    main()
