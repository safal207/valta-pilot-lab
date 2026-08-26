# Founding Pilot — Open Cart Email Sequence

Window: 2026-09-10 through 2026-09-16  
Capacity: three qualified founding slots  
Audience: responders, referrals, existing warm threads, and explicit opt-ins only

## Offer facts used in every message

```text
Offer: Zero / One / Unknown Payment Recovery Pilot
Price: USD 2,500
Payment: 50% to reserve, 50% on evidence delivery
Delivery: 10 business days after scope and access freeze
Scope: one bounded workflow, five agreed scenarios
Capacity: three founding slots
Communication: asynchronous by default
Access: sandbox, simulator, test ledger, test contract, or bounded authorized code path
```

Do not change price, capacity, or deadline inside the launch without documenting a real reason.

---

# Day 1 — Doors Open

## Subject

```text
Three Verified Transition pilot slots are open
```

## Email

Hi {{name/team}},

The founding window is now open for the **Zero / One / Unknown Payment Recovery Pilot**.

The pilot is for one narrow question:

> After timeout, retry, fallback, concurrency, or restart, can your team prove whether one bounded payment workflow produced zero, one, or an unresolved number of economic effects — and recover without guessing?

### What we will test

One payment, payout, escrow, or settlement workflow against five agreed scenarios, normally including:

1. stale authorization before dispatch;
2. action changed after approval;
3. concurrent duplicate attempts;
4. provider reports `accepted`, but the expected final state is absent;
5. timeout or restart after dispatch with unknown effect.

### What you receive

- lifecycle and invariant map;
- executable regression pack;
- separate decision, dispatch, and effect evidence;
- independently verifiable receipt bundle;
- concise finding and economic-risk readout;
- one bounded retest.

### Commercial boundary

```text
USD 2,500
50% to reserve the slot
50% on evidence delivery
10 business days after scope/access freeze
three founding slots
```

No production credentials or movement of real funds are required. This is not an unlimited audit, compliance certificate, or universal exactly-once guarantee.

To apply, reply with:

1. the single workflow;
2. the uncertain retry/recovery boundary;
3. the available test surface;
4. the independently observable final state;
5. the technical and budget owner.

I will confirm fit in writing before accepting payment.

Alexey Safonov

---

# Day 2 — “We Already Have Idempotency”

## Subject

```text
Idempotency can stop duplicates — but where does its proof end?
```

## Email

Hi {{name/team}},

A fair objection to this pilot is:

> “We already use idempotency keys.”

That may solve the problem — if the guarantee reaches the final economic boundary.

Five questions determine whether it does:

1. Does the same key reach every processor, fallback, and local rail?
2. Does each downstream system interpret the key for the same retention window?
3. Can a stale worker dispatch after a newer attempt owns the action?
4. Does provider acceptance prove settlement, or only request acceptance?
5. After a lost response, what evidence tells the system to retry, stop, or reconcile?

The pilot does not replace an idempotency mechanism that already works.

It tests and documents the boundary where that mechanism stops being provable.

The founding window remains open for three qualified workflows at USD 2,500 each.

Reply with the exact boundary of your idempotency guarantee, and I will tell you whether this pilot adds anything or would be redundant.

Alexey

---

# Day 3 — Evidence Demonstration

## Subject

```text
24 attempts. One owner. What happened to the money?
```

## Email

Hi {{name/team}},

A concurrency result from the current lifecycle is easy to summarize:

```text
24 execution attempts
1 durable reservation owner
23 stale or duplicate attempts rejected
```

That proves one part of the boundary: multiple callers cannot all own the same dispatch generation.

It does **not**, by itself, prove what happened externally.

The complete verdict also needs effect observation:

```text
accepted + observed expected effect -> VERIFIED
accepted + expected effect absent   -> UNVERIFIED
response lost after dispatch        -> RECONCILE_REQUIRED
```

That distinction is the product.

A system should not manufacture `SUCCESS` from a partial API response, and it should not manufacture “safe retry” from silence.

The founding pilot applies this lifecycle to one real sandbox or authorized test workflow and leaves executable evidence behind.

Three slots are available until the stated close date or until qualified capacity is filled.

Reply `scope` for the exact one-page boundary.

Alexey

---

# Day 4 — Fit / No Fit

## Subject

```text
This pilot is not for every payment team
```

## Email

Hi {{name/team}},

The Verified Transition pilot is a good fit when:

- one workflow moves or allocates real economic value;
- timeout, retry, fallback, concurrency, or restart can create uncertainty;
- a sandbox, simulator, test ledger, contract, or bounded code path exists;
- the final outcome can be observed independently;
- an engineering owner and a pilot budget exist.

It is not a fit when:

- the request is an unlimited audit;
- there is no authorized test surface;
- no independent final-state observer exists;
- the desired output is a compliance certificate;
- the team expects free custom engineering;
- the risk is already proven end to end by existing controls.

I would rather decline a poor fit than manufacture work.

For qualified teams, the founding pilot is USD 2,500 for one workflow and five agreed scenarios, delivered in 10 business days after scope and access are frozen.

Reply with a five-line workflow summary and I will answer `fit`, `not yet`, or `not needed` in writing.

Alexey

---

# Day 5 — Economic Case

## Subject

```text
What does one ambiguous payment incident cost your team?
```

## Email

Hi {{name/team}},

The pilot should not be justified with imaginary catastrophic-loss numbers.

Use your own operating facts:

```text
people involved in one reconciliation
x average hours
x loaded hourly cost
+ delayed funds or customer support cost
+ confirmed duplicate/incorrect payout exposure
+ engineering time needed to reproduce the incident
```

Then compare that with a USD 2,500 fixed-scope pilot that leaves reusable regression evidence.

The commercial question is not:

> “Could something terrible happen someday?”

It is:

> “Does this workflow currently consume enough money, time, or launch confidence to justify proving its recovery boundary once?”

If the answer is no, do not buy the pilot.

If the answer is yes, reply with the rough operating cost and the workflow. I will use only your supplied numbers in the scope and ROI readout.

Alexey

---

# Final Day — Morning

## Subject

```text
Founding pilot window closes today
```

## Email

Hi {{name/team}},

The founding window for the Zero / One / Unknown Payment Recovery Pilot closes today.

The offer remains:

```text
one bounded workflow
five agreed failure/recovery scenarios
executable evidence and one retest
USD 2,500
three founding capacity slots
```

Reply with the workflow, uncertain boundary, available test surface, observable final state, and owner. I will confirm fit before accepting payment.

Alexey

---

# Final Day — Objection Email

## Subject

```text
The strongest reason not to run this pilot
```

## Email

Hi {{name/team}},

The strongest reason not to run this pilot is simple:

> Your existing system already proves the full boundary.

That means it can show, after a lost response or restart:

- the exact authorized action;
- the one current dispatch owner;
- the downstream request identity;
- the independently observed economic result;
- the justified next action;
- a replayable evidence chain.

If you already have that, keep your money.

If one of those facts is inferred, manual, or distributed across teams, the founding pilot is designed to make that gap executable and testable.

The window closes today. Reply `boundary` if you want a written fit decision before close.

Alexey

---

# Final Hours

## Subject

```text
Closing the founding window
```

## Email

Hi {{name/team}},

The founding pilot window closes in a few hours.

I am closing it on schedule whether or not all three slots are filled. Any future opening will use a new scope and price decision rather than retroactive scarcity.

Reply now with the five qualification points if one bounded payment-recovery workflow is worth proving:

1. workflow;
2. uncertainty boundary;
3. test surface;
4. observable final state;
5. owner and budget.

Alexey

---

# Post-Close Responses

## Qualified but late

```text
Thanks — the founding window is closed, so I will not pretend the deadline was flexible.

Your workflow appears qualified. I can place it on the next-scope list and send the next commercial terms when a new capacity window is defined.
```

## Interested but no budget

```text
Thanks for being direct. I will keep this as product feedback rather than treat it as a sales opportunity.

A useful non-commercial contribution would be one anonymized failure state or an introduction to the person who owns payment reliability and budget.
```

## Wants a free custom test

```text
The public demo and self-test are free. A workflow-specific adapter, failure injection, evidence pack, and retest are the paid engagement.

I cannot build a custom pilot without a commercial scope.
```

## Wants a live call first

```text
I work asynchronously by default. Please send the workflow and the five qualification points in writing first.

If a live discussion is genuinely required after the boundary is frozen, we can decide that separately; it is not required to evaluate fit.
```
