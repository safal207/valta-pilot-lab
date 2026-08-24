# Valta Paid Pilot Offer v0.1

## Purpose

Prove or falsify whether Valta creates measurable economic value on one real financial workflow.

## Scope

One bounded workflow, for example:

```text
request -> authorization/policy check -> execution -> final economic state -> evidence
```

The customer and Valta agree on:

- one workflow;
- one economically meaningful risk;
- 3-5 failure/recovery scenarios;
- success evidence;
- a fixed pilot price;
- a clear end date or completion condition.

## Candidate failure scenarios

Depending on the system:

- timeout followed by retry;
- duplicate request;
- stale authorization;
- policy change between approval and execution;
- execution succeeds but local state reports failure;
- local state reports success but downstream execution is absent;
- concurrent actions exceed an intended limit;
- refund/reversal does not reconcile across views.

## Deliverables

1. Workflow and economic-risk map.
2. Agreed invariants.
3. Test/observation evidence for each scenario.
4. Reproducible failure path for any confirmed issue.
5. Protected-value / operational-savings estimate where evidence supports it.
6. Concise pilot ROI readout.
7. Recommendation: stop, iterate, or expand to recurring use.

## Initial price hypothesis

**$350-$750 fixed scope.**

This is a validation price, not the assumed long-term SaaS price.

## Expansion question

At the end of the pilot, ask one commercial question:

> If this control/evidence ran continuously on this workflow, would you pay for it on a recurring basis?

A successful pilot is not only a technical PASS. It produces evidence about willingness to pay and recurring value.
