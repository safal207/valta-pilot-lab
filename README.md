# Valta Pilot Lab

Valta Pilot Lab is a working repository for testing one core business hypothesis:

> Can a control and verification layer for AI-driven financial actions create measurable economic value for customers?

The goal is not to prove that the technology is interesting. The goal is to prove that a customer will pay for reduced financial loss, tighter authorization, safer retries, clearer reconciliation, and verifiable execution evidence.

## Current product decision

This repository is an **internal incubation and paid-pilot laboratory**. The public product name remains undecided pending naming and trademark review.

The selected v1 direction is a verified-transition control and evidence layer:

```text
exact authorization
  -> durable reservation
  -> dispatch
  -> observed economic effect
  -> safe recovery / reconciliation
  -> independently inspectable receipt
```

Read the product, technical, commercial, and 30-day execution decision:

- [`docs/verified-transition-mvp-v1.md`](docs/verified-transition-mvp-v1.md)

## Current thesis

A useful first customer is a team whose automated systems or AI agents can trigger money-moving or paid actions: paid APIs, wallets, payouts, escrow, settlement, or other financially meaningful operations.

The pilot should be evaluated against measurable outcomes:

- money under control;
- prevented unauthorized, duplicate, or policy-violating actions;
- reduced reconciliation and incident-response work;
- pilot price and delivery cost;
- customer ROI;
- willingness to continue on a recurring contract.

## Pilot loop

```text
one workflow
  -> one economic risk
  -> one bounded pilot
  -> measurable protected value
  -> evidence package
  -> recurring commercial decision
```

## Repository map

- `docs/verified-transition-mvp-v1.md` — selected product, architecture, business model, and execution plan.
- `docs/economic-model-v0.1.md` — first economic hypothesis.
- `docs/pilot-offer.md` — fixed-scope pilot offer.
- `docs/success-metrics.md` — evidence and ROI measurement.
- `pilots/_template.md` — reusable pilot worksheet.
- `mcp/README.md` — future ChatGPT / MCP integration boundary.
- `prototypes/README.md` — implementation experiments.

## Important

All pricing, ROI ratios, loss estimates, and market assumptions in this repository are hypotheses until validated with real paid pilot data.

Do not commit customer secrets, production credentials, wallet keys, API keys, private transaction data, or non-public infrastructure details.
