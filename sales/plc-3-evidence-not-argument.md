# PLC 3 — Evidence, Not an Argument

Target release: 2026-09-08  
Stage: Prelaunch Content 3 — Ownership Experience  
Primary format: email plus sample receipt

## Subject

```text
What if a payment incident ended with evidence, not an argument?
```

## Email

Hi {{name/team}},

After an ambiguous payment incident, several teams usually hold different pieces of reality:

- the policy service knows the action was allowed;
- the application knows it sent a request;
- the provider knows what it accepted;
- the bank, chain, or payout rail knows what settled;
- finance knows whether balances reconcile;
- support knows what the recipient reported.

The incident becomes expensive because nobody owns one evidence-bound answer.

The operating experience I am building toward is different.

For each logical action, the system ends with one justified state:

```text
BLOCKED             the exact action was not authorized
DUPLICATE           another attempt already owns or completed the action
VERIFIED            the expected economic effect was independently observed
UNVERIFIED          the claimed success is not supported by the observed result
RECONCILE_REQUIRED  the effect remains unknown or conflicting
```

And the receipt does not merely contain a final word. It binds the path:

```text
action identity and digest
-> policy decision
-> reservation owner and fencing generation
-> dispatch attempt
-> provider result
-> independent observation
-> final verdict and limitations
```

That changes the ownership experience:

### Before

```text
“Did it go through?”
“Probably.”
“Can we retry?”
“Let’s check three dashboards and ask finance.”
```

### After

```text
The action is VERIFIED.
Or it is explicitly RECONCILE_REQUIRED.
The old worker is fenced.
The evidence can be replayed.
The next allowed action is known.
```

This does not promise universal exactly-once execution. The guarantee remains bounded by the reservation store, adapter behavior, downstream idempotency, and completeness of the observer.

What it does provide is a testable, honest boundary instead of a success claim built from partial evidence.

On **September 10**, I will open **three founding pilot slots** for teams that want to pressure-test one bounded payment, payout, escrow, or settlement workflow.

The pilot will include:

- five agreed failure and recovery scenarios;
- executable invariants and regression tests;
- separate decision, dispatch, and effect evidence;
- an independently verifiable receipt bundle;
- a concise economic-risk readout;
- one bounded retest.

It will not require production credentials or movement of real funds.

**Reply `boundary` and I will send the one-page scope when the founding window opens.**

Alexey Safonov

## Sample receipt shape

Publish a real generated sample when available. The reader-facing summary should remain simple:

```json
{
  "action_id": "example-payout-001",
  "authorized_action_digest": "sha256:...",
  "reservation_generation": 1,
  "dispatch_attempts": 24,
  "active_dispatch_owners": 1,
  "provider_result": "ACCEPTED",
  "observed_effect": "MATCHED",
  "economic_effect_count": 1,
  "final_verdict": "VERIFIED",
  "receipt_integrity": "PASS",
  "limitations": [
    "sandbox adapter",
    "guarantee bounded by observer completeness"
  ]
}
```

Never fabricate an effect count or claim `VERIFIED` when the current executable demo does not support it.

## Qualification response to `boundary`

```text
Thanks — here is the fit check before I send a commercial scope.

1. What is the single workflow?
2. Where can timeout, retry, fallback, concurrency, or restart create uncertainty?
3. What sandbox, simulator, test ledger, test contract, or bounded code path is available?
4. What final state can be observed independently?
5. Who owns the technical decision and pilot budget?

If those five points are clear, I will freeze the pilot boundary in writing before accepting payment.
```
