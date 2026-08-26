# Opt-In Welcome Sequence

Status: copy-ready after a consent-aware endpoint is connected  
Audience: people who explicitly request the Ambiguous Payment Recovery Kit  
Maximum automatic educational follow-ups: **3**

## Consent boundary

Send this sequence only after explicit opt-in.

Every email must include a simple unsubscribe instruction. Stop automation when a reader replies, unsubscribes, bounces, or enters a direct qualification conversation.

Do not add cold contacts, support-ticket addresses, scraped emails, or a partner’s subscriber list.

## Day 0 — Deliver the kit

### Subject

```text
Your ambiguous-payment recovery kit
```

### Body

```text
Hi,

Here are the three resources you requested:

1. Seven-question Ambiguous Payment Recovery Self-Test
2. Cross-System Payment Proof Card
3. Machine-readable public sandbox result

Start with one sentence:

“The transition that becomes unknown is ________, and today the recovery
decision is owned by ________.”

The key distinction behind the kit is:

provider accepted
≠ external effect observed
≠ settlement final
≠ customer ledger reconciled
≠ safe to retry

Please do not send credentials, customer records, or non-public transaction
data. A high-level workflow is enough.

Reply with that one sentence if you want me to point to the most important
evidence boundary.

Alexey Safonov
Independent QA / financial-state verification

Unsubscribe: reply with “unsubscribe”.
```

## Day 2 — PLC 1: Accepted is not settled

### Subject

```text
The most expensive payment state is not failed
```

### Body

```text
A failed payment is usually visible.

The more expensive state is the one that looks partially successful:

provider: accepted
external rail: unknown
customer ledger: unknown
retry requested: yes

At that point, success and failure are not enough.

A safer system needs four outcomes:

VERIFIED — one matching effect is observed;
SAFE_TO_RETRY — zero effects are proven;
UNVERIFIED — acceptance exists, but the expected effect is absent;
RECONCILE_REQUIRED — an effect may have happened, so retry stays blocked.

Our public sandbox proof ran 24 retry attempts with one reservation owner,
23 rejected attempts, one external effect, one linked ledger posting, and a
receipt-integrity PASS.

That proves the declared sandbox boundary. It does not claim universal
exactly-once execution.

Which transition in your workflow becomes hardest to prove after timeout?

Alexey

Unsubscribe: reply with “unsubscribe”.
```

## Day 4 — PLC 2: Idempotency may protect the wrong boundary

### Subject

```text
Your idempotency key may protect the wrong boundary
```

### Body

```text
An idempotency key can be completely correct and still leave the global
economic outcome unknown.

It may deduplicate requests inside one provider while the full workflow crosses:

client or agent
→ provider
→ card, bank, or blockchain rail
→ recipient
→ customer ledger

Five responsibilities should stay separate:

1. evaluate the exact action;
2. reserve one execution owner;
3. fence stale dispatch attempts;
4. observe the external effect independently;
5. reconcile and finalize only from sufficient evidence.

The useful question is not “Do we have idempotency?”

It is:

“What exact boundary does the key protect, for how long, and what evidence
proves the irreversible effect outside that boundary?”

Reply with the provider or rail where your evidence stops. One line is enough.

Alexey

Unsubscribe: reply with “unsubscribe”.
```

## Day 7 — PLC 3: Ownership experience

### Subject

```text
Five tests before automation is allowed to retry money movement
```

### Body

```text
Before an automated workflow can safely retry, it should survive five tests:

1. stale authorization is blocked;
2. the action cannot change after approval;
3. concurrent retries produce one current execution owner;
4. provider acceptance without an external effect is not called success;
5. restart after dispatch cannot silently become a second effect.

The outcome should be one of:

VERIFIED
SAFE_TO_RETRY
UNVERIFIED
RECONCILE_REQUIRED

No hidden “probably failed, try again” state.

If one of these five tests maps to a real bounded workflow, reply with:

BOUNDARY: [workflow transition]
TEST SURFACE: [sandbox / simulator / test contract / code path]
OWNER: [team or role]

I’ll tell you whether it looks suitable for a small evidence-first pressure test.

Alexey

Unsubscribe: reply with “unsubscribe”.
```

## Qualification after a reply

Move out of automated education and ask only what is needed:

```text
1. What exact workflow is under control?
2. What evidence sources are available?
3. What happens today when outcome is unknown?
4. Is recovery automatic or manual?
5. How often does it occur?
6. Which team owns it?
7. Is there an authorized bounded test surface?
8. Is there budget for a fixed-scope pilot?
```

Do not reveal scarcity, price, or a sales deadline until workflow, owner, evidence, and budget are qualified.
