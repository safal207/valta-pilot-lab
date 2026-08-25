from decimal import Decimal

from ox_alpha import ProposedAction, evaluate_proposal, propose_action
from valta_verify import ActionLedger, Policy


def test_model_output_is_only_a_proposal() -> None:
    def fake_transport(payload, api_key):
        assert payload["model"] == "stealth/ox-alpha"
        assert api_key == "test-key"
        return {
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"actor":"agent-1","action":"pay","target":"vendor-a",'
                            '"amount":"25","action_id":"ox-001","policy_version":"v1",'
                            '"checked_at":"2026-08-25T12:00:00Z"}'
                        )
                    }
                }
            ]
        }

    proposal = propose_action(
        "Pay vendor-a $25",
        api_key="test-key",
        transport=fake_transport,
    )

    assert isinstance(proposal, ProposedAction)
    assert proposal.amount == Decimal("25")


def test_valta_blocks_model_proposal_that_exceeds_policy() -> None:
    proposal = ProposedAction(
        actor="agent-1",
        action="pay",
        target="vendor-a",
        amount=Decimal("250"),
        action_id="ox-002",
        policy_version="v1",
        checked_at="2026-08-25T12:00:00Z",
    )
    policy = Policy(
        version="v1",
        allowed_actions=frozenset({"pay"}),
        allowed_targets=frozenset({"vendor-a"}),
        max_amount=Decimal("100"),
    )

    decision = evaluate_proposal(proposal, policy, ActionLedger())

    assert decision.verdict == "BLOCK"
    assert decision.reason_code == "AMOUNT_EXCEEDS_POLICY"


def test_valta_allows_only_when_policy_itself_is_satisfied() -> None:
    proposal = ProposedAction(
        actor="agent-1",
        action="pay",
        target="vendor-a",
        amount=Decimal("25"),
        action_id="ox-003",
        policy_version="v1",
        checked_at="2026-08-25T12:00:00Z",
    )
    policy = Policy(
        version="v1",
        allowed_actions=frozenset({"pay"}),
        allowed_targets=frozenset({"vendor-a"}),
        max_amount=Decimal("100"),
    )

    decision = evaluate_proposal(proposal, policy, ActionLedger())

    assert decision.verdict == "ALLOW"
    assert decision.reason_code == "POLICY_SATISFIED"
    assert decision.execution_boundary == "EXTERNAL_UNVERIFIED"
