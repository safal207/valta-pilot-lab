# One Workflow. One Economic Failure Boundary. One Reproducible Answer.

## Fixed-Scope Economic Verification Pilot

Valta pressure-tests one consequential financial or agent-driven workflow and returns evidence your engineering team can reproduce.

This is not a broad audit, a request for production access, or an open-ended consulting engagement.

## 1. Control one exact workflow

Examples:

```text
fan payment -> creator earning -> payout -> reconciliation
```

or:

```text
funded escrow -> release / dispute -> final settlement
```

The workflow, test surface, completion condition, price, and delivery window are agreed before work begins.

## 2. Pressure-test the expensive boundary

The pilot selects 3–5 concrete failure or recovery paths, such as:

- ambiguous timeout followed by retry;
- duplicate or concurrent request;
- stale authorization after state change;
- release versus dispute race;
- refund or reversal crossing a payout boundary;
- local success with absent downstream execution;
- downstream success with unreconciled local state;
- replayed approval, permit, or settlement action.

## 3. Require one explainable economic result

The tested workflow must converge to a result that is consistent across the relevant views:

```text
request identity
+ authority / policy
+ state transition
+ observed execution
+ final balance / status
+ audit evidence
```

Authorization is not counted as proof of successful execution. Missing, stale, or conflicting evidence is surfaced explicitly.

## 4. Deliver evidence, not a generic report

The customer receives:

1. a bounded workflow and state-transition map;
2. agreed invariants;
3. reproducible traces for every scenario;
4. a shortest failing path for any confirmed issue;
5. recommended regression coverage;
6. a concise engineering summary;
7. an ROI readout using only customer-supported values.

No confirmed defect is required for the pilot to be useful: a passing result still produces reusable regression evidence for the tested boundary.

## 5. Fixed price and a clear next decision

### Creator payout / reconciliation

```text
Fixed fee: USD 500
Delivery: 3 business days after the bounded test surface is available
```

### Escrow release / dispute settlement

```text
Fixed fee: USD 750
Delivery: 3–5 business days after the bounded test surface is available
```

A sandbox, test contract, API surface, simulator, or bounded code path is sufficient. Broad production access is not required.

## Commercial success means one of four things

- a material failure or control gap is confirmed;
- supported recovery or operational savings exceed the pilot fee;
- the customer retains a new regression/control in CI;
- the customer asks to extend verification to recurring coverage or another workflow.

## The decision question

> If this control and evidence package ran continuously on the workflow, would the team pay to retain it as a recurring safeguard?

## Boundary

The pilot does not promise absolute safety, insurance, financial coverage, or a guaranteed defect. Prevented-loss and ROI numbers are reported only when supported by customer data and reproducible evidence.
