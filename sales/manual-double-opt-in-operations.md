# Manual Double Opt-In Operations

Status: active bridge until a server-side subscription provider is connected  
Canonical public site: https://ambiguous-payment-recovery-kit.lovable.app/  
Consent version: `v1.0-2026-08-26`

## Purpose

Operate the first consent-based subscribers safely without pretending that the current public site has an automated newsletter backend.

The live form opens a prefilled email. That first message is a **resource request**, not a confirmed subscription.

A subscriber enters the educational sequence only after a separate affirmative reply:

```text
CONFIRM
```

## Consent contract

The confirmation message must include this exact meaning:

> I want the Ambiguous Payment Recovery Kit plus no more than three educational follow-up emails. I can unsubscribe or request deletion at any time.

Record the consent version and confirmation timestamp before sending Day 0 resources.

## Gmail states

```text
Recovery Kit/00 Requests
Recovery Kit/10 Pending confirmation
Recovery Kit/20 Confirmed
Recovery Kit/30 Sequence active
Recovery Kit/90 Unsubscribed
Recovery Kit/99 Deletion
```

A message may move forward only when the evidence for the next state exists.

## Subscriber lifecycle

```text
REQUEST_RECEIVED
  -> CONFIRMATION_SENT
  -> CONFIRMED
  -> DAY_0_RESOURCES_SENT
  -> DAY_2_SENT
  -> DAY_4_SENT
  -> DAY_7_SENT
  -> COMPLETED
```

Suppression paths:

```text
UNSUBSCRIBE -> stop all future messages immediately
DELETE      -> stop messages and minimize/delete the registry record
BOUNCE      -> suppress the address
HUMAN STOP  -> suppress automation and handle manually
```

## Request intake

Search for:

```text
subject:"Ambiguous Payment Recovery Kit request"
```

Before responding:

- verify the message was actually sent by the requesting address;
- reject obvious automation, malformed requests, or unrelated content;
- do not accept credentials, payment data, production transaction records, or private customer evidence;
- capture only the minimum fields in the private consent registry;
- label the request `Recovery Kit/00 Requests`.

Minimum registry fields:

```text
work email
company (optional)
workflow answer (optional)
request timestamp
consent status and version
confirmation timestamp
partner ref and UTM attribution
sequence timestamps
unsubscribe / deletion state
operational notes
```

## Confirmation

Send the saved confirmation template.

Then label the thread:

```text
Recovery Kit/10 Pending confirmation
```

Do not send resources or educational content before the exact affirmative reply is received.

Generic responses must not reveal whether another address already exists in the registry.

## Confirmed subscriber

After a clear `CONFIRM` reply:

1. record `confirmed_at` and the consent version;
2. label the thread `Recovery Kit/20 Confirmed`;
3. send the Day 0 resource template;
4. set the next due action to Day 2;
5. move the thread to `Recovery Kit/30 Sequence active`.

## Educational sequence

The sequence is capped at exactly three educational follow-ups after Day 0:

| Step | Timing | Purpose |
|---|---:|---|
| Day 0 | after confirmation | deliver self-test, proof card, and public JSON |
| Day 2 | 2 days after Day 0 | PLC 1 — accepted is not settled |
| Day 4 | 4 days after Day 0 | PLC 2 — idempotency is not recovery |
| Day 7 | 7 days after Day 0 | PLC 3 — five tests and workflow boundary |

Before every send, check:

- no `UNSUBSCRIBE`, `DELETE`, bounce, complaint, or stop request;
- no human conversation that makes automation inappropriate;
- the previous step is recorded;
- the maximum follow-up count has not been exceeded.

After Day 7, mark the sequence complete. Do not continue automatically.

## Human reply rule

A meaningful reply about a real workflow exits the automated path.

Record the reply and move to manual qualification:

```text
exact workflow
systems / rails involved
unknown transition
current recovery method
automatic or manual reconciliation
frequency
investigation time
owner
authorized test surface
budget signal
```

Do not send a pilot price until the workflow and buyer are qualified.

## Unsubscribe

Any plain-language stop request counts; do not require the exact keyword.

Actions:

1. apply `Recovery Kit/90 Unsubscribed`;
2. remove active-sequence labels;
3. set suppression immediately;
4. record the timestamp;
5. send at most one short acknowledgement;
6. never send educational or promotional follow-up again unless the person later makes a fresh explicit request and confirms again.

## Deletion request

Any clear erasure request counts; do not require the exact keyword.

Actions:

1. apply `Recovery Kit/99 Deletion`;
2. suppress all sending immediately;
3. remove or minimize the registry record while retaining only what is strictly required to prove suppression, if applicable;
4. confirm completion without exposing internal data;
5. do not publish subscriber identities in GitHub, partner reports, demos, or screenshots.

## Partner attribution

Preserve:

```text
ref
utm_source
utm_medium
utm_campaign
```

Partners may receive aggregate reporting only:

```text
visits
resource requests
confirmed opt-ins
qualified workflow replies
paid-pilot deposits
collected attributable revenue
```

Do not share subscriber identities without separate explicit consent.

## Private registry

The operational registry is private and must not be committed to this repository.

Current implementation is a private Google Sheet with:

- Dashboard;
- Subscribers;
- Events;
- Sequence;
- Settings.

The repository documents the protocol only, not the people in it.

## Migration to automated backend

Replace this bridge only when the new system supports:

- server-side storage;
- double opt-in;
- single-use expiring confirmation tokens;
- rate limiting and bot controls;
- confirmed / unsubscribed / deleted suppression states;
- exactly three educational follow-ups after Day 0;
- unsubscribe and deletion handling;
- partner attribution;
- no secrets in frontend code;
- no disclosure of subscriber existence;
- export and audit restricted to an authenticated operator.

Run old and new systems in parallel for a small controlled test, reconcile counts, and only then retire the manual bridge.

## Non-claims

This process does not claim:

- a fully automated subscription backend;
- guaranteed delivery or inbox placement;
- production payment processing;
- universal exactly-once execution;
- compliance certification;
- subscriber, revenue, or ROI results that have not occurred.
