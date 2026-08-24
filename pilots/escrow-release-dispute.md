# Pilot: Escrow Release / Dispute Settlement

> Public template. Keep customer names, transaction data, credentials, and non-public architecture out of this repository.

## Customer / workflow

- Customer: `escrow / settlement platform`
- Workflow: `escrow created -> funded -> release/dispute decision -> final settlement state`
- Economic action: escrowed funds transition to released, refunded, or unresolved state
- Pilot price: **USD 750 fixed scope**

## Economic risk

Escrow is a stateful money flow where retries, stale decisions, concurrent actions, or disagreement between business state and fund movement can strand or misdirect value.

Primary risks:

- release after a dispute or stale decision;
- duplicate release/refund caused by retry or concurrent calls;
- funds become stuck in a state with no valid settlement path;
- ledger/audit state claims an outcome that actual fund movement did not reach;
- both sides observe incompatible final settlement state.

## Pilot scope

One bounded escrow lifecycle, four failure/recovery scenarios, and one evidence/economic readout.

### Scenarios

1. **Release vs dispute race**
   - release and dispute actions overlap or arrive from stale state;
   - verify only one valid economic transition can win.

2. **Ambiguous settlement result + retry**
   - release/refund is initiated;
   - downstream result is ambiguous;
   - retry occurs;
   - verify no duplicate value movement and final state converges.

3. **Stale authorization / decision**
   - an earlier release or settlement decision is replayed after the escrow state changed;
   - verify stale evidence cannot move funds.

4. **Liveness / recoverability**
   - exercise disputed or recovery state;
   - verify every state retaining escrowed value has an explicit path toward a valid final settlement or a clearly surfaced manual intervention state.

## Invariants

1. Escrowed value is conserved across funding, release, refund, fees, and final balances.
2. One escrow can settle economically at most once for the tested transition.
3. A disputed or superseded state cannot be bypassed by stale release evidence.
4. Business/audit state cannot claim settlement beyond observed execution evidence.
5. Every state holding customer funds exposes a valid recovery/settlement path or an explicit unresolved/manual state.

## Deliverables

- state-transition and economic-value trace;
- reproducible failure cases if found;
- evidence showing request identity, decision context, observed execution, and final state;
- regression/invariant recommendations;
- concise economic readout and limitations.

## ROI metric

Use only values supplied or supported by the customer.

```text
supported pilot value =
  confirmed wrong/duplicate settlement prevented
  + supported stranded-funds/recovery cost avoided
  + supported manual investigation cost avoided

ROI multiple = supported pilot value / 750
```

Supporting measurements:

- value represented by the tested escrow workflow;
- maximum value exposed by each identified failure path;
- operator/support time required for dispute and reconciliation today;
- number of controls/regressions retained after the pilot;
- customer willingness to extend coverage.

## Commercial success threshold

The pilot is commercially positive if it produces at least one of:

- a confirmed settlement/liveness failure with material economic exposure;
- supported avoided recovery/operations cost greater than the pilot price;
- a regression/control the customer adopts;
- agreement to expand into recurring settlement verification.

## Expansion hypothesis

If the bounded pilot validates value, expand into continuous governance/verification over escrow release, disputes, refunds, retries, and final reconciliation, with recurring pricing based on real workflow volume and observed value protected.
