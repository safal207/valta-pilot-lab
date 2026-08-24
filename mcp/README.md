# MCP / ChatGPT Integration Track

This track exposes the Valta pilot verifier to MCP-capable hosts without changing the underlying decision contract.

## Current prototype

Prototype 002 lives in `prototypes/verify_action/mcp_server.py` and uses the current stable MCP Python SDK v2.

It exposes one tool:

- `verify_action`

The tool accepts a proposed financial action plus an explicit prototype policy snapshot and returns structured decision evidence:

```text
ALLOW | BLOCK | INCONCLUSIVE
reason_code
policy_version
evidence_ref
execution_boundary
```

## Product objective

Let a user or agent ask Valta to evaluate a financially meaningful action without leaving the conversation.

```text
user/agent
  -> MCP verify_action
  -> Valta deterministic verifier
  -> allow/block/inconclusive
  -> evidence reference
```

## Run locally

From the repository root:

```bash
python -m pip install -r prototypes/verify_action/requirements-mcp.txt
python prototypes/verify_action/mcp_server.py
```

The server uses stateless Streamable HTTP with JSON responses. The decision path itself does not read wall-clock time.

For development with the MCP Inspector, the SDK CLI can also be installed with `mcp[cli]`.

## Prototype boundary

This is deliberately **not** production payment infrastructure.

- policy state is supplied explicitly for reproducibility;
- duplicate tracking uses an in-process prototype ledger;
- no wallet keys or real payment execution are present;
- `ALLOW` is a policy decision, not proof that downstream execution happened;
- `execution_boundary` remains `EXTERNAL_UNVERIFIED` unless observed evidence is explicitly supplied.

Production work must replace the in-memory ledger and caller-supplied policy with authenticated, durable Valta state before any exactly-once or live-freshness guarantee is made.

## Economic role

The ChatGPT/MCP integration is initially a distribution and demonstration surface, not the validated revenue model.

```text
try Valta in an existing AI environment
  -> identify a production-relevant workflow
  -> paid pilot
  -> measurable protected value / ROI
  -> recurring enterprise use
```

## Security notes

Never commit:

- production API keys;
- wallet keys or seed phrases;
- private customer policy data;
- privileged infrastructure endpoints;
- non-public transaction evidence.
