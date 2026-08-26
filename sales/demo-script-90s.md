# 90-Second Demo — The Proof Breaks Between Systems

## Goal

Show one bounded payment action across four independent boundaries:

```text
verified-transition lifecycle
payment provider
external recipient rail
customer accounting ledger
```

The demo does not ask the audience to trust a provider status or a slide. It produces an executable verdict and a receipt another process can verify.

## Run

From `prototypes/verify_action`:

```bash
python cross_system_demo.py --scenario concurrent-retry --format text
```

For the complete machine-readable evidence:

```bash
python cross_system_demo.py --scenario all --format json --include-receipt
```

## 0–12 seconds — The expensive unknown

**Narration**

> An automated payout is authorized and dispatched. The response disappears. The provider has one state, the external rail may have another, and the customer ledger may still be behind. Is retry safe — or does it pay twice?

**Screen**

```text
Payout: creator-218 / USD 5,000
Provider response: lost or ambiguous
Automation: retry requested
```

## 12–27 seconds — Permission is not execution

**Narration**

> The exact action passes policy, but `ALLOW` is only a decision. The runtime durably reserves one execution generation before any external effect is permitted.

**Screen**

```text
Decision: ALLOW
Action digest: sha256:...
Reservation owner: generation 1
Execution boundary: EXTERNAL_UNVERIFIED
```

## 27–47 seconds — Twenty-four retries, one owner

Run the concurrency scenario.

**Expected output**

```text
attempts=24
owner=1
rejected=23
```

**Narration**

> Twenty-four callers race after the timeout. Exactly one owns dispatch. Twenty-three stale or duplicate attempts are rejected before they can create another effect.

## 47–67 seconds — Observe three systems independently

**Narration**

> Reservation proves who may dispatch. It still does not prove what happened to the money. The observer reads the provider, the recipient rail, and the accounting ledger independently.

**Screen**

```text
provider: ACCEPTED
rail effects: 1
ledger effects: 1
linked rail credit: yes
```

## 67–82 seconds — The honest verdicts

**Narration**

> One linked rail and ledger effect becomes `VERIFIED`. A proven pre-effect rejection becomes `SAFE_TO_RETRY`. Provider acceptance without an external effect becomes `UNVERIFIED`. A split or unknown result becomes `RECONCILE_REQUIRED` — never a blind retry.

**Screen**

```text
VERIFIED
SAFE_TO_RETRY
UNVERIFIED
RECONCILE_REQUIRED
```

## 82–90 seconds — Evidence, not argument

**Narration**

> The final output is a hash-chained receipt and executable regression case. The pilot applies this proof to one bounded customer workflow without production funds or a universal exactly-once claim.

**Screen**

```text
economic_effects: 1
receipt_verified: true
bundle_digest: sha256:...
```

## Demo success criteria

- 24 attempts produce one reservation owner and 23 rejected attempts;
- the external rail records one economic effect;
- the customer ledger contains one linked posting;
- provider acceptance is never treated as sufficient settlement evidence;
- unknown post-dispatch state blocks blind retry;
- all four verdict families are reproducible;
- exported receipt verification passes;
- changed receipt content fails verification.

## What not to say

Do not claim:

- universal exactly-once execution;
- that every external rail supports the same idempotency or observation semantics;
- cryptographic authenticity beyond the implemented hash-chain integrity check;
- prevented-loss values without customer evidence;
- production readiness, custody, insurance, or compliance certification.
