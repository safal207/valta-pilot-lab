from __future__ import annotations

import json
import tempfile
from decimal import Decimal
from pathlib import Path

from action_lifecycle import (
    DISPATCH_ACCEPTED,
    OBSERVED_EXPECTED_EFFECT,
    VERIFIED,
    ActionLifecycle,
    SQLiteActionStore,
)
from valta_verify import ActionRequest, Policy


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
    action_id="demo-lifecycle-001",
    policy_version="policy-v1",
    checked_at="2026-08-24T09:00:00+00:00",
    authorization_expires_at="2026-08-24T10:00:00+00:00",
)

with tempfile.TemporaryDirectory() as tempdir:
    with SQLiteActionStore(Path(tempdir) / "actions.sqlite3") as store:
        lifecycle = ActionLifecycle(store)
        _, record = lifecycle.evaluate(request, policy)
        record = store.reserve(
            record.action_id,
            expected_version=record.version,
            evidence_at="2026-08-24T09:01:00+00:00",
            evidence={"owner": "demo-worker"},
        )
        record = store.mark_dispatching(
            record.action_id,
            expected_version=record.version,
            generation=record.generation,
            evidence_at="2026-08-24T09:02:00+00:00",
            adapter="sandbox-ledger-v1",
            downstream_idempotency_key=record.action_id,
        )
        record = store.record_dispatch_result(
            record.action_id,
            expected_version=record.version,
            generation=record.generation,
            evidence_at="2026-08-24T09:03:00+00:00",
            status=DISPATCH_ACCEPTED,
            downstream_request_id="sandbox-req-1",
        )
        record = store.begin_observation(
            record.action_id,
            expected_version=record.version,
            generation=record.generation,
            evidence_at="2026-08-24T09:04:00+00:00",
            evidence_source="sandbox-ledger",
        )
        record = store.record_observation(
            record.action_id,
            expected_version=record.version,
            generation=record.generation,
            evidence_at="2026-08-24T09:05:00+00:00",
            status=OBSERVED_EXPECTED_EFFECT,
            evidence_source="sandbox-ledger",
            evidence={"settled_amount": "25.00", "recipient": "vendor-a"},
        )
        store.finalize(
            record.action_id,
            expected_version=record.version,
            generation=record.generation,
            evidence_at="2026-08-24T09:06:00+00:00",
            final_verdict=VERIFIED,
        )
        print(json.dumps(store.export_receipt(request.action_id), indent=2, sort_keys=True))
