# Verified Transition Pilot — PLF Launch v1

Status: execution plan  
Campaign start: 2026-08-26  
Channel: email-first, asynchronous  
Initial offer: three paid founding-pilot slots

## 1. Launch decision

Use a Product Launch Formula-inspired sequence:

```text
pre-prelaunch: discover and name the expensive pain
        ↓
prelaunch: teach a new mechanism with executable proof
        ↓
launch: open a bounded paid engagement with a real close
```

The campaign does not sell a broad AI-safety platform, a processor, or a generic audit.

It sells one measurable outcome:

> Prove whether a financially meaningful automated action occurred zero, one, or multiple times; recover without guessing; and export evidence another party can inspect.

## 2. Buyer filter

A qualified account has:

- a live or production-relevant payment, payout, settlement, wallet, escrow, or paid-agent workflow;
- financial or operational cost when a result is ambiguous;
- a product, engineering, reliability, risk, or payments owner;
- an observable final state independent of the model or first API response;
- budget for QA, reliability, security, risk, or product validation;
- a bounded sandbox, simulator, test contract, or authorized source surface.

Disqualify or deprioritize when:

- the team has no budget and only wants free development;
- there is no owner for the failure boundary;
- the final economic effect cannot be observed;
- the request is an unlimited audit disguised as a small pilot;
- the buyer requires real-fund custody or unsupported guarantees;
- delivery would be mostly one-off integration with no reusable learning.

## 3. Positioning

### Category

**Verified Transition Infrastructure**

### First product

**Verified Transition Assurance Pilot**

### Core contrast

```text
authorization is not execution
accepted is not settled
idempotency is not reconciliation
an API status is not independent evidence
timeout is not proof of no effect
```

### One-sentence promise

> We pressure-test one financial workflow across authorization, dispatch, observed outcome, retry, and recovery, then deliver an executable regression pack and independently inspectable evidence bundle.

## 4. Phase 0 — pre-prelaunch

Dates: **August 26–31, 2026**

### Goal

Discover the buyer's exact language, ownership boundary, current workaround, and cost of ambiguity before presenting an offer.

### The shot-across-the-bow question

> If a financially meaningful action is dispatched, the client loses the response, and automation retries, can your team prove from independent evidence whether zero, one, or two economic effects occurred — and recover without guessing?

### Rules

- one company, one tailored question;
- plain text only;
- no attachment, demo link, calendar link, or proposal;
- no invented familiarity;
- no claim that the company has the bug;
- ask the correct team to route the question when using a public mailbox;
- accept a one-line answer: `yes`, `partly`, or `not yet`;
- do not debate a `yes`; ask what evidence closes the loop;
- no automatic chase inside 72 hours;
- do not contact multiple mailboxes at the same company in parallel.

### Pain variants

#### Payouts / marketplaces

> If a payout is dispatched, the response is lost, and the platform retries, can you prove whether the recipient received zero, one, or two payouts before finance reconciles it manually?

#### Fiat–stablecoin / multi-rail settlement

> If one rail appears complete while another is delayed or ambiguous, can you prove one economic outcome and safely choose retry, hold, or reconciliation?

#### Agent wallets / credentials

> If a single-use authority is consumed during an ambiguous checkout, can you prove both whether authority was consumed and whether payment occurred before issuing another credential?

#### Workflow protocols

> If a multi-step workflow times out after an irreversible step may have happened, can it resume from evidence without repeating the economic effect?

#### Paid tool calls / agent runtime

> If a paid capability times out after execution starts, can you prove whether the tool result and charge belong to the same attempt before the agent retries?

### Response classification

| Code | Signal | Next move |
|---|---|---|
| P1 | Explicit pain, manual reconciliation, incident, or uncertainty | Ask one cost/ownership question; invite to prelaunch list |
| P2 | Partly solved or guarantee depends on downstream system | Ask where evidence continuity breaks |
| P3 | Strong solved boundary with reproducible evidence | Learn the mechanism; possible partner, not immediate buyer |
| P4 | Relevant but no owner / routed internally | Wait for owner; one follow-up only |
| P5 | No budget or only wants free work | Keep as research contact; no custom build |
| P6 | Not relevant | Close cleanly |

### Qualification follow-up

Use only after a relevant reply:

> Thanks — where does the team feel the cost today: duplicate loss, manual reconciliation, incident investigation, delayed settlement, or blocked automation?

Then:

> Who owns that boundary, and is there a sandbox or bounded workflow where the failure can be reproduced without production funds?

### Phase-0 success gate

Do not begin the paid launch only because messages were sent.

Proceed when at least one of these is true:

- 5 qualified replies with repeated language around the same failure;
- 3 explicit statements of manual or financial cost;
- 2 workflow owners willing to inspect an executable demonstration;
- 1 buyer asks what a bounded test would cost.

If none occurs, change the segment or pain statement before creating more product.

## 5. Phase 1 — prelaunch content

Provisional dates: **September 1–6, 2026**

Final wording must reuse exact, non-confidential language from Phase 0 replies.

### PLC 1 — The hidden state after `accepted`

Purpose: reframe the problem.

Core lesson:

```text
provider accepted
≠ effect observed
≠ settlement final
≠ safe to retry
```

Suggested subject:

> The most expensive payment state is not failed

Content structure:

1. Start with an ambiguous timeout scenario.
2. Show why `success/failed` is an incomplete model.
3. Introduce `RECONCILE_REQUIRED` as an honest third state.
4. Give one diagnostic question the reader can run internally.
5. Open loop: next message explains why ordinary idempotency is not enough.

CTA:

> Reply with the transition in your stack that becomes hardest to prove after a timeout.

### PLC 2 — Why idempotency is not recovery

Purpose: teach the mechanism.

Core lesson:

- idempotency can prevent duplicate handling inside a declared boundary;
- it cannot by itself prove whether an external irreversible effect occurred;
- durable reservation, fencing, observation, and reconciliation are separate responsibilities.

Suggested subject:

> Your idempotency key may be protecting the wrong boundary

Use the lifecycle:

```text
EVALUATE
→ RESERVE
→ DISPATCH
→ OBSERVE
→ RECONCILE
→ FINALIZE
```

Show three outcomes:

```text
known no effect  → safe release under policy
known effect     → observe and finalize
unknown effect   → reconcile; never retry blindly
```

Open loop: next message demonstrates the five scenarios used to falsify a workflow.

### PLC 3 — The five-scenario proof

Purpose: transfer ownership and demonstrate proof.

Suggested subject:

> Five tests before an agent is allowed to move money

Scenarios:

1. stale authorization;
2. action changed after approval;
3. concurrent duplicate retry;
4. provider `accepted`, final state absent;
5. timeout after dispatch with unknown outcome and restart.

Show what the evidence bundle contains:

- canonical action digest;
- policy and authorization evidence;
- reservation and fencing generation;
- dispatch record;
- independent effect observation;
- final verdict and explicit limitations;
- executable regression test.

CTA:

> Reply `BOUNDARY` with one workflow you would want tested against these five scenarios.

## 6. Phase 2 — launch

Provisional open: **September 7, 2026**  
Provisional close: **September 12, 2026, 17:00 ET**, or when three slots are contracted.

Do not claim scarcity unless delivery capacity is genuinely limited to three slots.

### Offer

**Verified Transition Assurance Pilot**

```text
Price: USD 2,500
Payment: 50% to reserve the slot, 50% on delivery
Scope: one bounded workflow
Scenarios: up to five agreed failure/recovery cases
Mode: asynchronous; no live meeting required
Delivery: target seven business days after complete authorized access
Environment: sandbox, simulator, test contract, or bounded source path
```

### Deliverables

- workflow and invariant map;
- executable failure scenarios;
- deterministic verdicts and explicit uncertainty states;
- portable evidence bundle;
- regression pack;
- concise findings and remediation notes;
- one retest of agreed fixes within scope;
- ROI readout separating confirmed facts from estimates.

### Non-claims

The pilot does not provide:

- custody or movement of real funds;
- a universal exactly-once guarantee;
- a formal security or compliance certification;
- an unlimited smart-contract audit;
- production incident response;
- unsupported claims about prevented loss;
- free custom product development.

### Launch sequence

#### L1 — Open

Subject:

> Three verified-transition pilot slots are open

Message jobs:

- connect the Phase-0 pain to the five-scenario mechanism;
- state scope, price, capacity, and boundary;
- invite a reply with `PILOT` and the workflow name;
- no calendar call required.

#### L2 — Proof and fit

Subject:

> What the pilot proves — and what it deliberately does not

Cover:

- one concrete receipt bundle;
- restart and concurrent-retry evidence;
- exact non-claims;
- who should and should not buy.

#### L3 — Objections / FAQ

Subject:

> Do we need production access or real funds?

Answer:

- no real funds required;
- no secrets committed;
- asynchronous delivery is supported;
- an observable final state is required;
- unsupported boundaries become explicit `UNVERIFIED` or `RECONCILE_REQUIRED`.

#### L4 — 24-hour close

Subject:

> Pilot intake closes tomorrow at 17:00 ET

State only factual capacity and remaining slots.

#### L5 — Close

Subject:

> Verified Transition Pilot intake is closed

Close at the stated time. Do not manufacture a late exception. Keep qualified non-buyers for the next cohort.

## 7. Economics

### Founding cohort

```text
3 pilots × $2,500 = $7,500 booked revenue
```

Track:

- delivery hours per pilot;
- reusable adapter/test/evidence code;
- customer-specific work;
- gross contribution;
- confirmed manual effort reduced;
- confirmed incident or duplicate class discovered;
- expansion or recurring signal.

### Price gate

Raise the standard pilot to **$5,000+** when two of these are true:

- a reusable adapter covers most of the workflow;
- delivery stays within the target effort;
- the buyer requests a second workflow;
- evidence is used in a release, audit, or incident process;
- the buyer asks for recurring coverage.

Never keep a low founding price for a buyer without budget. A discount buys learning, access, proof, or reference value — not vague enthusiasm.

## 8. Funnel metrics

Track by company, not by mailbox.

| Stage | Primary metric |
|---|---|
| Qualified account | Has flow, cost, owner, evidence boundary, and budget potential |
| Question delivered | Valid business address; no bounce |
| Meaningful reply | Answers the boundary, not an automated support response |
| Pain confirmed | Names cost, manual work, uncertainty, or blocked automation |
| Prelaunch engaged | Replies to PLC or requests proof |
| Pilot qualified | One bounded workflow and authorized test surface |
| Commercial | Price and payment terms accepted |
| Expanded | Second workflow, recurring coverage, or referral |

Useful rates after enough volume:

```text
meaningful reply rate
pain-confirmation rate
qualified-pilot rate
paid conversion rate
gross contribution per pilot
expansion rate
```

Do not optimize opens. Optimize qualified conversations and paid proof.

## 9. Operational rules

- Gmail label for the first stage: `PLF/0 Pre-Prelaunch`.
- Keep all replies in the original thread.
- Create a new company thread only when no relevant thread exists.
- Never send parallel cold messages to multiple people at the same company.
- Use the respondent's own words in later content only when non-confidential and paraphrased.
- Do not expose customer names, incidents, or internal architecture without permission.
- Stop active pursuit after a clear `no`.
- No free implementation for research contacts without budget.

## 10. Immediate execution checklist

- [x] Merge the durable action lifecycle into `main`.
- [x] Start question-first pre-prelaunch outreach.
- [x] Label first-stage Gmail threads.
- [ ] Collect and classify replies as P1–P6.
- [ ] Identify the repeated expensive pain.
- [ ] Build one evidence bundle around that exact pain.
- [ ] Write PLC 1 using the market's language.
- [ ] Send PLC 1 only to relevant contacts and permissioned/warm threads.
- [ ] Complete PLC 2 and PLC 3.
- [ ] Open three paid slots only after the Phase-0 gate is met.
- [ ] Require payment to reserve a launch slot.
- [ ] Close at the stated deadline and publish an evidence-based campaign review.
