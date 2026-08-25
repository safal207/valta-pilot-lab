# Buyer-Ready Pilot Kit

This folder turns the Valta economic-verification model into a small customer-facing sales package.

## Assets

- [`pilot-one-pager.md`](pilot-one-pager.md) — the first document to send when a product, payments, security, or engineering owner asks what the pilot actually is.
- [`demo-script-90s.md`](demo-script-90s.md) — a short recorded or live demonstration of allow, block, replay, and outcome separation.
- [`sample-assurance-bundle.json`](sample-assurance-bundle.json) — an illustrative machine-readable request, decision, and outcome bundle.
- [`roi-readout-template.md`](roi-readout-template.md) — the commercial evidence sheet completed at the end of a pilot.

## Recommended sequence

```text
initial interest
-> one-page pilot offer
-> 90-second demonstration
-> agree exact workflow and test surface
-> fixed-scope paid pilot
-> ROI/evidence readout
-> recurring-control decision
```

## What may be tailored

For each prospect, change only:

1. the exact workflow;
2. the economic failure boundary;
3. the fixed scenarios;
4. the price and delivery window;
5. the ROI metric supported by the customer’s own data.

## Invariants that must not be weakened

- A decision for action A cannot authorize action B.
- A stale or replayed approval cannot move value.
- Authorization does not prove successful execution.
- A downstream claim of success requires observed outcome evidence.
- Missing or conflicting evidence is surfaced, not silently converted into success.
- Prevented-loss and ROI numbers are never invented.

## Public-repository boundary

Keep customer names, credentials, non-public architecture, transaction data, private correspondence, and production evidence out of this repository. The sample bundle is illustrative and is not a production signature, attestation, insurance promise, or guarantee of absolute safety.
