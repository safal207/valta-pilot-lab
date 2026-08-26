# Zero / One / Unknown Payment Recovery Pilot

## One Workflow. Five Failure Boundaries. One Reproducible Answer.

The pilot pressure-tests one financially meaningful automated workflow and answers a narrow question:

> After timeout, retry, fallback, concurrency, or restart, can the team prove whether zero, one, or an unresolved number of economic effects occurred — and recover without guessing?

This is not a broad audit, a request for production access, a compliance certificate, or an open-ended consulting engagement.

## 1. Freeze one exact workflow

Examples:

```text
invoice approval
-> vendor payout
-> provider response
-> external settlement
-> reconciliation
```

```text
creator earning
-> platform allocation
-> payout dispatch
-> recipient credit
-> refund / chargeback reconciliation
```

```text
funded escrow
-> release or dispute
-> settlement
-> final balances
```

Before payment, both sides agree in writing on:

- the workflow;
- five scenarios;
- the authorized test surface;
- evidence sources;
- completion condition;
- exclusions;
- delivery and retest boundary.

## 2. Pressure-test five expensive boundaries

The default scenarios are:

1. stale authorization before dispatch;
2. amount, recipient, target, or action changed after approval;
3. duplicate and concurrent attempts;
4. provider reports `accepted`, but the expected final state is absent;
5. timeout or restart after dispatch with an unknown effect.

A workflow-specific scenario may replace a default one when agreed before delivery begins.

## 3. Separate permission from economic reality

The pilot reconstructs the complete transition:

```text
exact action and identity
+ authority and policy evidence
+ durable execution ownership
+ dispatch attempt
+ provider / transport result
+ independently observed economic effect
+ justified recovery or final verdict
```

The final state is explicit:

```text
BLOCKED
DUPLICATE
VERIFIED
UNVERIFIED
RECONCILE_REQUIRED
```

Authorization is not counted as execution. Provider acceptance is not counted as settlement. Timeout is not counted as proof of no effect.

## 4. Deliver executable evidence

The customer receives:

1. bounded lifecycle and invariant map;
2. executable regression pack for the five scenarios;
3. decision, reservation, dispatch, observation, and finalization evidence;
4. shortest failing path for any confirmed issue;
5. independently verifiable receipt bundle;
6. concise engineering and economic-risk readout;
7. one bounded retest of agreed fixes.

No confirmed defect is required for the pilot to be useful. A passing result still creates reusable evidence for the tested boundary.

## 5. Founding commercial terms

```text
Fixed fee: USD 2,500
Payment: 50% to reserve the slot, 50% on evidence delivery
Delivery: 10 business days after scope and access are frozen
Capacity: three founding slots
Communication: asynchronous by default
```

Suitable test surfaces include:

- sandbox;
- simulator;
- test ledger;
- test smart contract;
- bounded API;
- authorized repository path.

Production credentials and movement of real funds are not required.

After the three founding slots, a comparable standard pilot is expected to start at USD 5,000, subject to the adapter and workflow scope.

## Qualification

A good fit has:

- financially meaningful state transitions;
- a retry, fallback, settlement, reconciliation, or stale-authority risk;
- an observable final state;
- an authorized test surface;
- a technical owner;
- a pilot budget.

Not a fit:

- unlimited audit scope;
- no independently observable outcome;
- no authorized test environment;
- request for free custom engineering;
- requirement for custody, real-money execution, insurance, or certification;
- a boundary already proven end to end by existing controls.

## Application by email

Send:

1. the single workflow;
2. the uncertain failure/recovery boundary;
3. the available test surface;
4. the independently observable final state;
5. the technical and budget owner;
6. the desired start date.

Fit is confirmed in writing before payment is accepted.

## Evidence and ROI boundary

The pilot does not promise absolute safety, universal exactly-once execution, insurance, financial coverage, or a guaranteed defect.

Prevented-loss and ROI figures are reported only when supported by customer data and reproducible evidence. The economic readout keeps separate:

- confirmed prevented loss;
- supported operational savings;
- protected value under control;
- unresolved or unquantified risk.

## Expansion decision

At delivery, the customer chooses one of four outcomes:

- stop: the tested boundary does not justify further spend;
- fix and retest: a confirmed issue needs remediation;
- extend: another workflow has the same pattern;
- retain: recurring assurance or release-by-release regression coverage is justified.
