# JV Partner Kit — Ambiguous Payment Recovery

Status: ready for individual partner conversations  
Goal: borrow trusted attention while building a consent-based owned audience  
Canonical live destination: **https://ambiguous-payment-recovery-kit.lovable.app/**

## Partnership principle

A partner does **not** transfer an email list.

The partner recommends a useful diagnostic to an audience that already opted in to hear from them. Interested readers visit the public page and voluntarily request the kit. Subscriber identities are not shared back to the partner; aggregate attribution may be reported.

```text
partner trust
→ useful diagnostic
→ voluntary opt-in
→ educational sequence
→ qualified workflow
→ bounded paid pilot
```

## Best partner profiles

Prioritize people or organizations with an audience of:

- payment and financial-infrastructure engineers;
- agent-framework builders whose agents call paid tools or move value;
- fintech, stablecoin, wallet, escrow, payout, or marketplace operators;
- reliability, risk, reconciliation, and finance-operations leaders;
- security or QA practitioners working on financial state transitions.

A small, relevant, trusted audience is more valuable than a large generic one.

## Core message

> A provider can prove its own request state. The harder question is whether one economic outcome can be proven across the provider, external rail, recipient, and customer ledger before an automated retry is permitted.

## Destination link

Use one stable partner slug and channel-specific UTM values:

```text
https://ambiguous-payment-recovery-kit.lovable.app/?ref={{partner_slug}}&utm_source={{channel}}&utm_medium=partner&utm_campaign=ambiguous-payment-recovery
```

Examples:

```text
https://ambiguous-payment-recovery-kit.lovable.app/?ref=ganiyu&utm_source=newsletter&utm_medium=partner&utm_campaign=ambiguous-payment-recovery

https://ambiguous-payment-recovery-kit.lovable.app/?ref=community-x&utm_source=telegram&utm_medium=partner&utm_campaign=ambiguous-payment-recovery

https://ambiguous-payment-recovery-kit.lovable.app/?ref=podcast-y&utm_source=podcast&utm_medium=partner&utm_campaign=ambiguous-payment-recovery
```

## One-line mention

> Can your payment workflow prove zero, one, or unknown economic effects after a timeout? This free seven-question recovery self-test shows where retry becomes guesswork: {{partner_link}}

## 90-word newsletter block

> A payment provider can accurately report that a request was accepted while the complete economic outcome remains unknown across the external rail, recipient, and customer ledger. That gap becomes dangerous when automation retries after timeout. Alexey Safonov built a public diagnostic and executable sandbox proof around four honest outcomes: `VERIFIED`, `SAFE_TO_RETRY`, `UNVERIFIED`, and `RECONCILE_REQUIRED`. The headline test ran 24 retry attempts with one reservation owner, 23 rejected attempts, one rail effect, and a verified receipt. Take the seven-question recovery self-test here: {{partner_link}}

## 300-word newsletter block

### The payment state between success and failure

A failed payment is usually visible. The more expensive state is one that looks partially successful.

An automated payout is authorized. The provider accepts the request. The caller loses the response or restarts. The external rail may already have credited the recipient. The customer ledger may still be delayed. Automation requests a retry.

At that point:

```text
provider accepted
≠ recipient credited
≠ settlement final
≠ customer ledger reconciled
≠ safe to retry
```

An idempotency key may protect one service boundary. A webhook may accurately report the provider's local state. Neither automatically proves the complete economic result across every system involved.

A safer model needs four explicit outcomes:

- `VERIFIED` — one matching external effect and linked ledger result are observed;
- `SAFE_TO_RETRY` — a pre-effect rejection and zero external effects are proven;
- `UNVERIFIED` — the provider claims acceptance, but the expected effect is absent;
- `RECONCILE_REQUIRED` — an effect may have occurred or evidence disagrees, so blind retry remains blocked.

The public sandbox proof behind this diagnostic ran 24 concurrent retry attempts. One durable reservation owner was established, 23 stale or duplicate attempts were rejected, one external rail effect was observed, one linked ledger posting was observed, and the exported receipt passed integrity verification.

That proves the declared sandbox boundary. It does not claim universal exactly-once execution across arbitrary providers or rails.

The free kit includes a seven-question self-test, one-page proof card, and machine-readable public result:

{{partner_link}}

## Social post

> “Accepted” is not the same as settled — and timeout is not proof that nothing happened. This seven-question recovery self-test identifies where evidence breaks between provider, rail, recipient, and ledger: {{partner_link}}

## Subject lines

```text
The payment state between success and failure
Can your workflow prove what happened after timeout?
“Accepted” is not settlement
Your idempotency key may protect the wrong boundary
Zero, one, or unknown economic effects?
```

## Podcast / webinar angles

1. **Why accepted is the most dangerous payment status for autonomous systems**
2. **Idempotency is not recovery: the evidence boundary between provider and settlement**
3. **How to block an AI-agent retry without pretending the first payment failed**
4. **Provider, rail, ledger: who owns the unknown state?**
5. **From policy ALLOW to observed economic outcome**

## Co-authored technical lesson

Recommended title:

> **Policy ALLOW is not settlement: how an agent recovers without paying twice**

Suggested roles:

```text
partner:
framework, policy, wallet, or payment-domain context

Verified Transition Lab:
durable reservation, fenced dispatch, independent observation,
reconciliation verdict, and reproducible receipt
```

The material should show one complete failure path, not a generic product tour.

## CTA

Primary:

> Take the seven-question Ambiguous Payment Recovery Self-Test.

Secondary after a qualified reply:

> Which transition in your workflow becomes impossible to prove automatically after the response disappears?

Do not lead with price, a calendar link, or a long product pitch.

## Recommended referral economics

These are negotiating defaults, not public promises:

```text
Qualified warm introduction:
15% of the first collected project payment

Co-authored material + audience distribution + qualification:
20% of the first collected project payment
```

Conditions:

- applies only to a genuinely new lead sourced by the partner;
- paid only after customer funds clear;
- applies to the first project only unless separately agreed;
- no lifetime commission;
- no commission on existing pipeline or prior contacts;
- no transfer of subscriber lists;
- no offset against unrelated debts or prior obligations;
- no ownership of core IP;
- scope, attribution window, and payout terms must be written before launch.

## Partner preflight

Before distribution, confirm:

- the public URL loads without authentication or 404;
- the audience opted in to hear from the partner;
- the topic is relevant to that audience;
- the partner slug is unique;
- all download and privacy links work;
- the copy contains no unsupported customer, ROI, or prevented-loss claim;
- subscriber emails are not shared;
- the material says sandbox proof, not universal guarantee;
- educational follow-up is capped and includes a clear exit path.

## Reporting

Report aggregate metrics only:

```text
unique partner visits
opt-in requests
self-test replies
qualified workflow conversations
requests for executable proof
paid-pilot deposits
collected revenue attributable to partner
```

Do not report individual subscriber identities without explicit consent.

## Initial outreach message to a potential partner

```text
I’m not asking you to promote a startup or hand over a list.

I have a short diagnostic for teams that handle payment retries, payouts,
wallets, escrow, or agent-initiated purchases: can the workflow prove zero,
one, or unknown economic effects after a timeout?

I will provide the complete copy, proof card, public sandbox result, and a
partner-attributed opt-in link. Your audience gets a useful self-test; people
who want the material request it directly and can leave at any time.

Would this be relevant enough for one educational mention or co-authored
technical note?
```

## Hosting note

The Lovable URL above is the canonical live destination. A GitHub Pages mirror may be enabled later, but partner campaigns must not use the mirror until it has been verified publicly.
