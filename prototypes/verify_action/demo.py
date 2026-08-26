import json
from decimal import Decimal

from action_lifecycle import ActionLedger
from valta_verify import ActionRequest, Policy, action_digest, verify_action


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

with ActionLedger() as store:
    decision = verify_action(request, policy, store)
    evaluated = store.get(request.action_id)
    reserved = store.reserve_if_version_matches(
        action_id=request.action_id,
        action_digest=action_digest(request),
        expected_version=evaluated.version,
        reserved_at="2026-08-24T09:01:00+00:00",
        reservation_expires_at="2026-08-24T09:05:00+00:00",
    )
    dispatching = store.mark_dispatch_started(
        action_id=request.action_id,
        expected_version=reserved.version,
        generation=reserved.generation,
        started_at="2026-08-24T09:02:00+00:00",
        adapter="demo-sandbox-ledger",
        downstream_idempotency_key=request.action_id,
    )
    dispatched = store.record_dispatch_result(
        action_id=request.action_id,
        expected_version=dispatching.version,
        generation=dispatching.generation,
        status="ACCEPTED",
        observed_at="2026-08-24T09:02:10+00:00",
        downstream_request_id="demo-request-001",
    )
    verified = store.record_observation(
        action_id=request.action_id,
        expected_version=dispatched.version,
        generation=dispatched.generation,
        status="MATCHED",
        observed_at="2026-08-24T09:02:20+00:00",
        evidence_ref="demo-ledger:entry-001",
    )
    store.finalize_if_version_matches(
        action_id=request.action_id,
        expected_version=verified.version,
        generation=verified.generation,
        finalized_at="2026-08-24T09:02:30+00:00",
        final_verdict="VERIFIED",
    )
    print(
        json.dumps(
            {
                "decision": decision.to_dict(),
                "receipt": store.export_receipt(request.action_id),
            },
            indent=2,
            sort_keys=True,
        )
    )
