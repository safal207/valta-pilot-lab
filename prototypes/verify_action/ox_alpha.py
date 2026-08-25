from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable

from valta_verify import ActionLedger, ActionRequest, Decision, Policy, verify_action

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "stealth/ox-alpha"


@dataclass(frozen=True)
class ProposedAction:
    actor: str
    action: str
    target: str
    amount: Decimal
    action_id: str
    policy_version: str
    checked_at: str
    authorization_expires_at: str | None = None

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "ProposedAction":
        required = {"actor", "action", "target", "amount", "action_id", "policy_version", "checked_at"}
        missing = sorted(required - value.keys())
        if missing:
            raise ValueError(f"missing proposed-action fields: {', '.join(missing)}")
        return cls(
            actor=str(value["actor"]),
            action=str(value["action"]),
            target=str(value["target"]),
            amount=Decimal(str(value["amount"])),
            action_id=str(value["action_id"]),
            policy_version=str(value["policy_version"]),
            checked_at=str(value["checked_at"]),
            authorization_expires_at=(
                None if value.get("authorization_expires_at") is None else str(value["authorization_expires_at"])
            ),
        )

    def to_request(self) -> ActionRequest:
        return ActionRequest(
            actor=self.actor,
            action=self.action,
            target=self.target,
            amount=self.amount,
            action_id=self.action_id,
            policy_version=self.policy_version,
            checked_at=self.checked_at,
            authorization_expires_at=self.authorization_expires_at,
            execution_observed=False,
        )


Transport = Callable[[dict[str, Any], str], dict[str, Any]]


def _default_transport(payload: dict[str, Any], api_key: str) -> dict[str, Any]:
    request = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def propose_action(
    instruction: str,
    *,
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
    transport: Transport = _default_transport,
) -> ProposedAction:
    key = api_key or os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is required")

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Return only JSON for one proposed financial action. "
                    "Required keys: actor, action, target, amount, action_id, policy_version, checked_at. "
                    "Optional key: authorization_expires_at. "
                    "Do not return ALLOW/BLOCK and do not claim authorization; Valta decides separately."
                ),
            },
            {"role": "user", "content": instruction},
        ],
        "response_format": {"type": "json_object"},
    }
    response = transport(payload, key)
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("unexpected OpenRouter response shape") from exc

    if not isinstance(content, str):
        raise ValueError("model content must be a JSON string")
    return ProposedAction.from_mapping(json.loads(content))


def evaluate_proposal(proposal: ProposedAction, policy: Policy, ledger: ActionLedger) -> Decision:
    """Valta is the sole authority for the final verdict.

    The model proposes an action only. Its wording, reasoning, or any attempted
    authorization claim is never used as an authorization signal.
    """

    return verify_action(proposal.to_request(), policy, ledger)
