# PLC 1 — Accepted Is Not Settled

Status: **ready for the permissioned prelaunch list**  
Stage: opportunity / problem reframing  
Audience: relevant responders, referrals, routed human owners, and explicit opt-ins  
Commercial offer: **not revealed in this asset**

## Purpose

Help a payment, reliability, product, or engineering owner recognize one expensive state that ordinary `success / failed` models hide:

> A provider accepted the request, but the complete economic outcome is not yet proven across the provider, external rail, recipient, and customer ledger.

This material must deliver useful diagnostic value before asking for a sale.

## Recommended subject

```text
The most expensive payment state is not failed
```

Alternatives:

```text
Your provider said “accepted.” Did the money move exactly once?

The payment state between success and failure
```

## Email-ready PLC

Hi {{name/team}},

A failed payment is usually visible.

The more expensive state is the one that looks partially successful.

Imagine this sequence:

```text
1. An automated payout is authorized.
2. The provider receives and accepts the request.
3. The caller loses the response or restarts.
4. The external rail may already have credited the recipient.
5. The customer ledger may still be delayed or unreconciled.
6. Automation requests a retry.
```

At that point, `success` and `failed` are not enough.

The evidence may look like this:

```text
Provider:        ACCEPTED
External rail:   UNKNOWN
Customer ledger: UNKNOWN
Retry requested: YES
```

An idempotency key may protect one service boundary. A webhook may describe the provider’s latest state. Neither automatically proves the complete economic result across every system that matters.

A safer recovery model needs four honest outcomes:

```text
VERIFIED
One matching economic effect is independently observed.
Finalize the action.

SAFE_TO_RETRY
A pre-effect rejection and zero external effects are proven.
A new attempt may be permitted under policy.

UNVERIFIED
The provider claims acceptance, but the expected external effect is absent.
Do not claim success.

RECONCILE_REQUIRED
An effect may have occurred, or the evidence domains disagree.
Block blind retry until the state is reconciled.
```

The key distinction is simple:

```text
provider state
≠ external economic effect
≠ customer-ledger reconciliation
```

I built a deterministic proof around this boundary. In its concurrency scenario:

```text
24 retry attempts
1 durable reservation owner
23 stale or duplicate attempts rejected
1 external rail effect
1 linked customer-ledger posting
receipt verification: PASS
```

That result proves the declared sandbox boundary. It does **not** claim that every provider or rail offers universal exactly-once execution.

### Seven-question ambiguous-payment self-test

1. Is authorization bound to the exact amount, recipient, target, and action?
2. Is one execution owner durably reserved before dispatch?
3. Can an old worker be fenced after a timeout or restart?
4. Is provider `accepted` kept separate from settlement finality?
5. Can the external economic effect be observed independently?
6. Does an unknown outcome block blind retry?
7. Can another process replay the evidence and reach the same verdict?

One “no,” “unknown,” or “we check that manually” identifies the transition worth pressure-testing.

Which transition in your workflow becomes hardest to prove after a timeout?

A one-line answer is enough.

Alexey Safonov  
Independent QA / financial-state verification

---

## Short version

Use only when the recipient has asked for a concise explanation.

```text
A provider can prove its own request state. That does not always prove the complete economic result across the external rail and the customer ledger.

After an ambiguous timeout, the safe outcomes are:

VERIFIED — one effect is proven;
SAFE_TO_RETRY — zero effects are proven;
UNVERIFIED — acceptance exists, but the expected effect does not;
RECONCILE_REQUIRED — the effect may have happened, so retry stays blocked.

Our current sandbox proof ran 24 concurrent retries with one reservation owner, 23 rejected attempts, one rail effect, one linked ledger posting, and a verifiable receipt.

Which transition in your workflow becomes “unknown” after a timeout?
```

## Public article version

### The most expensive payment state is not failed

Payment systems are usually described with a reassuring binary:

```text
success
failed
```

But distributed money movement contains a third state:

```text
an irreversible effect may have happened,
but the available evidence does not yet prove the complete outcome
```

This state appears when a request crosses multiple independently operated boundaries:

```text
client or agent
→ payment provider
→ external banking / card / blockchain rail
→ recipient
→ customer accounting ledger
```

Each component can accurately report its own local state while the global economic result remains uncertain.

A provider response of `accepted` can mean that the request passed a local boundary. It does not necessarily prove that the recipient received the funds, that the external rail reached finality, or that the customer ledger reconciled the same effect.

This is why the safe recovery question is not merely:

> Did the API call succeed?

It is:

> What independent evidence justifies retry, finalization, or reconciliation now?

A useful verdict model is:

| Verdict | Evidence | Permitted action |
|---|---|---|
| `VERIFIED` | One matching external effect and linked ledger result | Finalize |
| `SAFE_TO_RETRY` | A pre-effect rejection and zero external effects | Retry under policy |
| `UNVERIFIED` | Acceptance exists but the expected effect is absent | Do not claim success |
| `RECONCILE_REQUIRED` | Evidence is incomplete, conflicting, or split across systems | Block blind retry |

The operational advantage is not magical certainty. It is refusing to manufacture certainty from partial evidence.

A system becomes safer when it can say:

```text
I know the effect happened.
I know the effect did not happen.
I do not yet know — therefore I will not repeat it blindly.
```

## Proof behind the lesson

The executable demo used by this PLC is in:

- [`../prototypes/verify_action/cross_system_demo.py`](../prototypes/verify_action/cross_system_demo.py)
- [`../prototypes/verify_action/cross_system_proof.py`](../prototypes/verify_action/cross_system_proof.py)
- [`demo-script-90s.md`](demo-script-90s.md)
- [`proof-card-cross-system-payment.md`](proof-card-cross-system-payment.md)

Reproduce the headline scenario:

```bash
cd prototypes/verify_action
python cross_system_demo.py --scenario concurrent-retry --format text
```

Generate all machine-readable scenarios and receipt bundles:

```bash
python cross_system_demo.py --scenario all --format json --include-receipt
```

## Open loop into PLC 2

PLC 2 answers the natural objection:

> “We already use idempotency keys. Isn’t that enough?”

The next lesson separates five responsibilities:

```text
evaluation
reservation
fenced dispatch
independent observation
reconciliation / finalization
```

## Personalization rule

Before sending, change only:

- the opening workflow example;
- the names of the relevant systems or rails;
- the final diagnostic question.

Do not claim that the recipient has a defect or incident unless they have said so.

## Non-claims

This PLC does not claim:

- universal exactly-once execution;
- production custody or movement of real funds;
- that provider acceptance is false or useless;
- that all webhook or idempotency designs are incomplete;
- formal security, accounting, or compliance certification;
- prevented-loss values without customer evidence;
- that an automated observer can close an evidence domain it cannot actually access.

## Send gate

Send the full PLC only to:

- a person who answered the initial question;
- a human owner to whom the question was routed;
- a referral;
- an existing warm thread;
- someone who explicitly asked for the proof or prelaunch material.

Do not send the full PLC sequence to an unresponsive cold address.
