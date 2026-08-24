# Valta Economic Model v0.1

Status: hypothesis, not validated economics.

## 1. First economic beachhead customer

Target teams where automated software or AI agents can trigger financially meaningful actions without continuous manual supervision.

Good first workflows include:

- paid API or tool calls;
- wallet execution;
- payouts;
- escrow release;
- settlement;
- refunds or reversals;
- automated purchasing;
- other actions where retry, stale state, policy mismatch, or duplicate execution can create economic loss.

The first customer should have all three:

1. a real money-moving or paid workflow;
2. a failure mode with measurable economic consequences;
3. enough operational frequency to observe the workflow during a bounded pilot.

## 2. What protected value means

`Protected value` is the economic value Valta can credibly attribute to controlling, blocking, proving, or simplifying a financial action.

Potential components:

- prevented duplicate spend;
- prevented unauthorized spend;
- prevented policy-violating spend;
- prevented execution after stale authorization;
- avoided unreconciled or ambiguous financial state;
- reduced manual reconciliation effort;
- reduced incident investigation effort;
- reduced expected loss from a known failure path.

Protected value must be tied to observable evidence. A hypothetical catastrophic loss should not be counted as realized protected value unless the pilot design justifies an expected-value calculation.

## 3. What the customer would pay

Initial pricing is a hypothesis.

A first pilot should be deliberately small, bounded, and paid. A working starting range is:

- fixed-scope pilot: **$350-$750**;
- one production-relevant workflow;
- a small set of agreed failure/recovery scenarios;
- concise evidence package and ROI readout.

The pilot price is not the long-term product price.

If the pilot proves recurring value, the commercial model can evolve toward:

- monthly enterprise subscription;
- usage-based pricing tied to governed actions;
- a hybrid subscription + usage model;
- ecosystem / marketplace economics where appropriate.

## 4. How ROI is measured in a pilot

Core measurements:

### Money under control

Total economic value associated with actions observed or governed during the pilot.

### Prevented loss

Value of duplicate, unauthorized, policy-violating, or otherwise invalid actions that were demonstrably blocked or neutralized.

### Operational savings

Estimated cost of reconciliation, investigation, manual approval, or recovery work removed by the control/evidence layer.

### Pilot cost

What the customer paid for the pilot plus any material customer-side integration effort that should be acknowledged.

### ROI hypothesis

```text
ROI multiple = measurable protected value / pilot cost
```

This ratio is useful only when both numerator and denominator are explained and evidence-backed.

## 5. Evidence needed before a serious investor conversation

Target proof package:

- 3 paid pilots;
- real production-relevant workflows;
- documented money under control;
- observed failure/risk scenarios;
- evidence of protected value or operational savings;
- price paid by each customer;
- delivery cost / gross-margin estimate;
- customer willingness to continue, expand, or repeat;
- at least one strong case study that can be explained without hand-waving.

The desired investor story is:

> Here is the customer. Here is the financial workflow. Here is the value at risk. Here is what Valta controlled or protected. Here is what the customer paid. Here is the resulting margin and expansion path.

## Falsification criteria

This model should be considered weakened if repeated pilots show that:

- customers acknowledge the risk but will not pay to control it;
- integration cost exceeds protected value;
- the relevant failures are too rare to measure or price;
- customers prefer existing wallet/payment controls and see no incremental value;
- evidence/auditability is valued but not enough to drive a recurring contract.

The purpose of v0.1 is to discover this quickly, not to defend the hypothesis.
