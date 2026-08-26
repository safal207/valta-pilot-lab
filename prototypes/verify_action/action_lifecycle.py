from __future__ import annotations

from lifecycle_store import SQLiteActionStore
from lifecycle_types import *  # noqa: F403 - intentional public re-export
from lifecycle_types import __all__ as _lifecycle_type_exports
from valta_verify import ActionRequest, Decision, Policy, verify_action


class ActionLifecycle:
    """Orchestration facade that keeps model proposals out of authorization."""

    def __init__(self, store: SQLiteActionStore) -> None:
        self.store = store

    def evaluate(
        self,
        request: ActionRequest,
        policy: Policy,
    ) -> tuple[Decision, ActionRecord]:  # noqa: F405 - re-exported contract type
        decision = verify_action(request, policy, self.store)
        if decision.reason_code in {"DUPLICATE_ACTION_ID", "ACTION_DIGEST_MISMATCH"}:
            return decision, self.store.get_action(request.action_id)
        return decision, self.store.record_evaluation(request, decision)


__all__ = [*_lifecycle_type_exports, "SQLiteActionStore", "ActionLifecycle"]
