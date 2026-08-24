import json
from decimal import Decimal

from valta_verify import ActionLedger, ActionRequest, Policy, verify_action


policy = Policy(
    version="policy-v1",
    allowed_actions=frozenset({"pay"}),
    allowed_targets=frozenset({"vendor-a"}),
    max_amount=Decimal("100.00"),
)

request = ActionRequest(
    actor="demo-agent",
    action="pay",
    target="vendor-a",
    amount=Decimal("25.00"),
    action_id="demo-action-001",
    policy_version="policy-v1",
    checked_at="2026-08-24T09:00:00+00:00",
    authorization_expires_at="2026-08-24T10:00:00+00:00",
)

decision = verify_action(request, policy, ActionLedger())
print(json.dumps(decision.to_dict(), indent=2, sort_keys=True))
