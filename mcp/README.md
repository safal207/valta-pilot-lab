# MCP / ChatGPT Integration Track

This directory is reserved for the smallest useful Valta integration surface for ChatGPT and other MCP-capable agent environments.

## Product objective

Let a user or agent ask Valta to evaluate a financially meaningful action without leaving the conversation.

Example interaction:

```text
user/agent -> Valta tool -> policy/authorization evaluation -> allow/block -> evidence
```

## Minimal tool surface

Potential first tools:

- `check_policy`
- `verify_action`
- `get_proof`

Do not add payment execution until the control and evidence contract is clear.

## First demo target

A convincing first demo should show:

1. one requested action;
2. the relevant policy/context;
3. an allow or block decision;
4. evidence explaining the decision;
5. a clear boundary between decision evidence and actual downstream execution.

## Economic role

The ChatGPT/MCP integration is initially treated as a distribution and product-demonstration surface, not as the validated revenue model.

The intended funnel is:

```text
try Valta in an existing AI environment
  -> identify a production-relevant workflow
  -> paid pilot
  -> measurable ROI
  -> recurring enterprise use
```

## Security notes

Never commit:

- production API keys;
- wallet keys or seed phrases;
- private customer policy data;
- privileged infrastructure endpoints;
- non-public transaction evidence.
