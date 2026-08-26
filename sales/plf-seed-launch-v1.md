# Verified Transition Pilot — PLF-Style Seed Launch v1

Status: execution plan  
Launch owner: Alexey Safonov  
Primary channel: asynchronous email  
Campaign start: 2026-08-26  
Public product name: TBD after naming review

## 1. Launch objective

Sell one to three paid design-partner engagements for a narrow financial-control outcome:

> Prove whether a bounded automated payment workflow produced zero, one, or an unresolved number of economic effects after timeout, retry, fallback, concurrency, or restart — and leave an executable regression pack plus independently inspectable evidence.

The launch is successful only when a qualified company pays. Replies, praise, GitHub stars, introductions, and technical curiosity are useful signals but are not revenue validation.

## 2. Audience

Primary buyers:

- payment-infrastructure engineering leaders;
- payment orchestration and reliability leaders;
- payout and creator-platform engineering leaders;
- API bank and embedded-finance product leaders;
- agentic-finance, wallet, and delegated-spend teams;
- escrow, settlement, and reconciliation owners.

A qualified prospect has:

- real or production-relevant money movement;
- a retry, fallback, settlement, reconciliation, or stale-authorization boundary;
- a sandbox, simulator, test ledger, bounded API, or authorized code path;
- an engineering owner;
- budget for reliability, QA, security, or payments operations.

Do not optimize the campaign for builders without budget. They may provide feedback or introductions, but they do not set the roadmap.

## 3. The big idea

```text
AUTHORIZED does not mean EXECUTED.
ACCEPTED does not mean SETTLED.
TIMEOUT does not mean NO EFFECT.
RETRY does not mean SAFE RETRY.
A LOG does not prove COMPLETE ECONOMIC REALITY.
```

The painful question behind the launch:

> After an ambiguous payment result and a retry, can your team prove whether zero, one, or two economic effects occurred — and recover without guessing?

## 4. Unique mechanism

The product mechanism is a verified-transition lifecycle:

```text
EVALUATE
  -> RESERVE
  -> DISPATCH
  -> OBSERVE
  -> RECONCILE
  -> FINALIZE
```

It separates:

1. exact-action authorization;
2. durable ownership of the dispatch boundary;
3. provider or transport response;
4. independent observation of economic effect;
5. explicit uncertainty and reconciliation;
6. final evidence receipt.

The mechanism is already represented by the durable lifecycle merged into `main`. The launch does not wait for custom hardware, a new protocol, or a broad platform rewrite.

## 5. Offer

### Founding offer

**Zero / One / Unknown Payment Recovery Pilot**

```text
Price: USD 2,500
Capacity: 3 founding slots
Delivery: 10 business days after access and scope are complete
Payment: 50% to reserve the slot, 50% on evidence delivery
Communication: asynchronous by default
Environment: sandbox, simulator, test contract, or bounded authorized code path
```

### Included

- one bounded payment, payout, escrow, or settlement workflow;
- lifecycle and invariant map;
- five agreed failure/recovery scenarios;
- executable regression pack;
- evidence bundle distinguishing decision, dispatch, observation, and finalization;
- independent receipt verification;
- concise finding and economic-risk readout;
- one bounded retest of agreed fixes.

### Default scenarios

1. stale authorization before dispatch;
2. amount, target, or action changed after approval;
3. concurrent duplicate attempts;
4. provider reports `accepted`, but the expected final state is absent;
5. timeout or restart after dispatch with unknown effect.

### Excluded

- custody or movement of real customer funds;
- unlimited security audit;
- production credentials;
- formal compliance certification;
- universal exactly-once claims;
- insurance or guaranteed prevention of loss;
- unrelated refactoring;
- live meetings as a delivery requirement.

### Standard price after founding slots

The next comparable pilot should start at USD 5,000 when the adapter, observer, and evidence format are reusable.

## 6. Ethical PLF adaptation for B2B outreach

Product Launch Formula is designed around an audience that has chosen to hear from the seller. Do not send the complete multi-email launch sequence to an unresponsive cold address.

Use two lanes:

### Cold discovery lane

- one personalized painful question;
- one concise follow-up only;
- no price, calendar link, attachment, or broad product pitch in the first message;
- move the contact to the launch lane only after a reply, referral, or explicit request for more information.

### Warm launch lane

Use the full Prelaunch Content and Open Cart sequence only for:

- responders;
- referrals;
- existing warm threads;
- people who explicitly request the materials;
- subscribers or followers who opted in.

## 7. Phase 1 — Pre-Prelaunch

Dates: 2026-08-26 through 2026-09-01

Goals:

- create anticipation around a newly executable recovery boundary;
- learn the exact language buyers use for the pain;
- separate policy problems from outcome/reconciliation problems;
- discover the objections that PLC must answer;
- build a small warm list before revealing the offer.

Jeff Walker's useful Pre-Prelaunch principle is to ask the audience for questions and feedback before presenting the offer. For this B2B campaign, use one sharp failure question first, then ask for their two biggest questions only after engagement.

### First-touch template

Subject:

```text
One painful question about [specific payment boundary]
```

Body:

```text
Hi [team/name],

One question from an independent QA engineer studying [their specific payment boundary]:

[One concrete zero/one/two-effects question tied to their public product.]

No pitch attached; I’m mapping which payment stacks can already answer this deterministically and where the real gap remains.

Alexey Safonov
```

### Pain-question patterns

#### Agentic finance

> If an agent receives a valid policy ALLOW, the request times out after dispatch, and it retries under the same policy, can you prove whether zero, one, or two economic effects occurred — not merely that both attempts were policy-compliant?

#### API bank

> When a client submits an ACH, RTP, or FedNow payment, loses the response after dispatch, and retries, what evidence tells it whether to retry, reconcile, or stop without risking a second economic effect?

#### Payment orchestration

> When smart routing receives an ambiguous result from one processor and falls back to another, what prevents the original and fallback attempts from both settling, and how does the merchant prove the final outcome?

#### Payout platform

> If a creator or vendor payout times out after dispatch and the platform retries, can it prove the recipient received exactly one payout across the processor state and its own ledger — or detect uncertainty before a second payout?

#### Mass payments

> During a partial batch failure, if one transfer was dispatched but its response was lost, how does the client distinguish a safe retry from duplicate-payment risk and prove the final effect count?

### Follow-up after a meaningful reply

```text
Thanks — that is exactly the boundary I am mapping.

What are the two hardest questions your team still has about proving or recovering this state: one technical and one operational/economic?

I have an executable lifecycle for the problem now. I am not sending an offer yet; I want the next material to answer the real questions rather than the questions I imagine teams have.
```

### Reply classification

| Signal | Meaning | Next action |
|---|---|---|
| "We already use idempotency keys" | Possible partial solution | Ask whether the downstream rail honors the key and how an unknown result is reconciled |
| "We rely on webhooks" | Outcome may still be incomplete | Ask about delayed, duplicated, missing, or out-of-order webhooks |
| "We reconcile manually" | Confirmed operational pain | Ask hours per incident/month and which team owns it |
| "This cannot happen" | Possible blind spot or strong guarantee | Ask for the declared boundary and failure behavior after provider timeout |
| "Talk to engineering/payments" | Routing success | Continue in-thread; do not restart cold outreach |
| No reply | No evidence | Send one follow-up, then stop |

### Pre-Prelaunch success threshold

- 20 highly qualified first touches;
- at least 4 substantive replies or internal routes;
- at least 2 confirmed manual-reconciliation or ambiguous-outcome pains;
- at least 1 prospect requesting the executable model or pilot details.

The first six messages were sent on 2026-08-26 and are tracked privately in Gmail under:

```text
PLF/Verified Transition/Pre-Prelaunch
```

Do not publish recipient addresses or private replies in this public repository.

## 8. Phase 2 — Prelaunch Content

Use three short, consumable pieces released over 6–10 days. Each piece must be valuable without purchase and must answer objections discovered during Pre-Prelaunch.

### PLC 1 — The Opportunity

Target date: 2026-09-02

Title:

> Your payment API said “accepted.” Did the money move exactly once?

Purpose:

- name the hidden gap;
- show why local API success and global economic correctness differ;
- reveal the opportunity: make uncertainty explicit before it becomes loss or manual reconciliation.

Core story:

```text
An automated payment is authorized.
The provider receives it.
The caller loses the response.
The caller retries.
Both requests can look locally reasonable.
Only the final economic state tells the truth.
```

Free value:

**Seven-question Ambiguous Payment Self-Test**

1. Is authorization bound to the exact action parameters?
2. Is an execution owner durably reserved before dispatch?
3. Can a stale process be fenced after recovery?
4. Does provider acceptance remain separate from settlement?
5. Can the final effect be observed independently?
6. Does unknown outcome block blind retry?
7. Can another party replay the evidence and reach the same verdict?

CTA:

> Reply with the one step in your flow where the answer is “unknown” or still manual.

### PLC 2 — The Transformation

Target date: 2026-09-04

Title:

> How to recover from a timeout without paying twice

Purpose:

- show the mechanism rather than claim magic;
- demonstrate the state change from guesswork to controlled recovery;
- answer “we already have retries/idempotency/webhooks.”

Content:

```text
Before:
ALLOW -> send -> timeout -> retry/guess

After:
EVALUATE -> RESERVE -> DISPATCH -> OBSERVE
                         |           |
                         |           +-> VERIFIED / UNVERIFIED
                         +-> UNKNOWN -> RECONCILE_REQUIRED
```

Demonstrate:

- 24 concurrent attempts;
- one reservation owner;
- stale generations rejected;
- accepted-without-effect becomes `UNVERIFIED`;
- unknown post-dispatch result becomes `RECONCILE_REQUIRED`;
- no blind second dispatch.

Free value:

A small failure-injection checklist that teams can run against their own workflow.

CTA:

> Send one anonymized state transition; I will reply with the first invariant I would test.

### PLC 3 — The Ownership Experience

Target date: 2026-09-08

Title:

> What it feels like when a payment incident ends with evidence, not an argument

Purpose:

- show the final operating experience;
- reveal what the paid pilot includes;
- establish the exact claim boundary;
- announce the opening date and three-slot capacity.

Show the final receipt states:

```text
VERIFIED
BLOCKED
UNVERIFIED
DUPLICATE
RECONCILE_REQUIRED
```

Show what the buyer owns after the pilot:

- executable invariants;
- regression tests;
- evidence bundle;
- declared guarantee boundary;
- known unknowns;
- retest path.

Pre-frame:

> On September 10, I will open three founding slots for one bounded workflow each. This is for teams with a real retry/reconciliation boundary and a sandbox or authorized test surface. It is not a broad audit or a request for production keys.

CTA:

> Reply `boundary` to receive the one-page scope before the slots open.

## 9. Phase 3 — Open Cart

Dates: 2026-09-10 through 2026-09-16

Capacity: three founding slots

Only send this sequence to warm or opted-in contacts.

### Day 1 — Doors open

Subject:

> Three Verified Transition pilot slots are open

Message structure:

- restate the zero/one/unknown pain;
- state the 10-business-day transformation;
- list included deliverables;
- state USD 2,500 price and 50/50 payment terms;
- link or attach the one-page scope only when requested;
- ask for a short written description of the workflow.

### Day 2 — Objection: “We already use idempotency”

Explain that idempotency can be necessary without proving:

- the key reached every downstream boundary;
- two providers share the same semantics;
- an old process is fenced;
- settlement was independently observed;
- a timeout is safe to retry.

### Day 3 — Evidence demonstration

Show one concise artifact:

```text
24 attempts
1 reservation owner
1 observed effect
23 stale/duplicate attempts rejected
receipt verified independently
```

Do not claim this automatically generalizes to every payment rail.

### Day 4 — Who it is and is not for

Good fit:

- one bounded money-moving state machine;
- observable final outcome;
- engineering owner;
- willingness to test failures;
- budget.

Bad fit:

- unlimited audit request;
- no authorized surface;
- no final-state observer;
- desire for a compliance certificate;
- expectation of free custom engineering.

### Day 5 — Economic case

Ask the buyer to compare the pilot price with:

- one duplicate or incorrect payout;
- one manual reconciliation incident;
- engineering time spent proving what happened;
- delay in safely automating the workflow.

Do not invent savings. Use only buyer-supplied values.

### Final day

Use honest capacity and deadline:

- morning: deadline reminder;
- afternoon: answer the strongest objection discovered during the launch;
- final hours: short close notice.

Do not manufacture scarcity. If a slot remains open after the stated close, end the founding launch and reopen later under a new, honest condition.

## 10. Cart-close handling

A buyer applies by email with:

1. workflow summary;
2. failure boundary;
3. test environment available;
4. final state that can be independently observed;
5. technical owner;
6. desired start date.

Qualification response:

```text
Thanks. Based on the written boundary, this appears [qualified / not yet qualified].

Before accepting payment, I will freeze:
- the exact workflow;
- five scenarios;
- evidence sources;
- access limits;
- delivery and retest boundary.

No production credentials or real-fund access are required.
```

## 11. Metrics

### Funnel

Track privately:

```text
qualified contacts
-> delivered first touches
-> substantive replies
-> pain confirmed
-> PLC requested/consumed
-> scope requested
-> qualified applications
-> deposits paid
-> pilots delivered
-> expansion or recurring signal
```

### Decision metrics

Continue the offer when:

- at least one paid pilot closes;
- multiple prospects describe the same pain in their own words;
- delivery creates a reusable adapter, observer, or test pattern;
- a buyer requests a second workflow or recurring coverage.

Narrow the offer when:

- buyers pay for independent testing but not runtime integration;
- each workflow is unique but the failure-testing method is reusable.

Stop or reposition when:

- qualified teams agree the risk exists but repeatedly will not pay;
- integration cost exceeds supported value;
- final economic state cannot be observed;
- existing controls already prove the full boundary.

## 12. Message discipline

Always lead with:

- one concrete failure;
- one expensive uncertainty;
- one question.

Do not lead with:

- “causal processor”;
- a list of repositories;
- consciousness or living systems;
- FPGA/ASIC plans;
- generic AI safety;
- a long biography;
- price before pain is acknowledged.

Commercial translation:

```text
Causal processing
-> no state transition without evidence and authority

Living system
-> observes, remembers, detects uncertainty, and recovers safely

T-Trace / CML / LiminalDB / CaPU
-> evidence, ancestry, durable lifecycle, and controlled execution
```

## 13. Launch assets checklist

- [ ] Pre-Prelaunch reply log and pain-language summary
- [ ] PLC 1 email/post and seven-question self-test
- [ ] PLC 2 executable demo and failure-injection checklist
- [ ] PLC 3 sample receipt and ownership-experience email
- [ ] One-page pilot scope
- [ ] Written qualification form
- [ ] Payment and delivery terms
- [ ] Three-slot capacity tracker
- [ ] Evidence readout template
- [ ] Post-launch review: what buyers said, paid, rejected, or ignored

## 14. Source principles

This campaign adapts Jeff Walker's published Product Launch Formula structure:

- Pre-Prelaunch builds anticipation and requests audience feedback;
- three staggered Prelaunch Content pieces communicate opportunity, transformation, and ownership experience;
- Open Cart is a limited, honest sales window;
- value is delivered before revealing the offer;
- desire and clarity are developed before availability.

References:

- [The Four Key Steps Behind My Product Launch Process](https://jeffwalker.com/product-launch-process/)
- [My Secrets to Consistent Success with Product Launch Formula](https://jeffwalker.com/my-secrets-to-consistent-success-with-product-launch-formula/)
- [A Simple Marketing Strategy Focused on the Fundamental](https://jeffwalker.com/a-simple-marketing-strategy-focused-on-the-fundamental/)

This repository and campaign are not affiliated with Jeff Walker or Product Launch Formula.
