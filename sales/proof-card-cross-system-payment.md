# The Proof Breaks Between Systems

## Cross-System Payment Recovery — Proof Card

> A provider can prove its own request state. The hard part is proving one economic outcome across the provider, external rail, recipient, and customer ledger before retrying.

## The expensive state

```text
Payment action:   authorized and dispatched
Provider:         ACCEPTED or response lost
External rail:    unknown or delayed
Customer ledger:  unknown or unreconciled
Automation:       requests retry
```

A retry is safe only when the evidence justifies it.

```text
API accepted
≠ recipient credited
≠ settlement final
≠ ledger reconciled
≠ safe to retry
```

## What the proof observes

The demo keeps four boundaries separate:

```text
verified-transition lifecycle
        ↓
sandbox payment provider
        ↓
external recipient rail
        ↓
customer accounting ledger
```

The independent observer reads provider, rail, and ledger evidence separately. It never treats provider acceptance as settlement proof by itself.

## Four honest verdicts

| Verdict | What the evidence shows | Recovery decision |
|---|---|---|
| `VERIFIED` | One matching rail credit and one linked ledger posting | Finalize; do not retry |
| `SAFE_TO_RETRY` | Explicit pre-effect rejection and zero external effects | A new attempt may be permitted under policy |
| `UNVERIFIED` | Provider accepted, but no expected external effect appeared | Do not claim success; investigate the missing effect |
| `RECONCILE_REQUIRED` | An effect may have happened, or evidence domains disagree | Block blind retry until reconciliation |

## Executable headline result

```text
SCENARIO: SETTLED_AND_RECONCILED
VERDICT: VERIFIED

provider:          ACCEPTED
retry attempts:    24
reservation owner: 1
rejected attempts: 23
rail effects:      1
ledger effects:    1
receipt verified:  true
```

The concurrency control proves that one attempt owns the dispatch generation. The independent observation proves what happened outside that control boundary.

Both are required.

## Why ordinary controls may stop too early

### Authorization

Proves the action was allowed under a policy.

It does not prove the action executed.

### Idempotency key

Can deduplicate processing inside a declared service and retention window.

It does not automatically prove that every fallback provider, external rail, recipient, and customer ledger share the same key or semantics.

### Webhook

Can report a provider state transition.

It may be duplicated, delayed, out of order, missing, or limited to the provider’s own evidence domain.

### Accounting ledger

Can record the customer’s financial view.

It may lag the external rail or contain a posting that still needs to be linked to the exact dispatch attempt.

## Reproduce it

From the repository root:

```bash
cd prototypes/verify_action
python cross_system_demo.py --scenario concurrent-retry --format text
```

Run all verdict families:

```bash
python cross_system_demo.py --scenario all --format text
```

Export complete machine-readable receipts:

```bash
python cross_system_demo.py \
  --scenario all \
  --format json \
  --include-receipt > cross-system-proof.json

python -m json.tool cross-system-proof.json > /dev/null
```

Run the regression suite:

```bash
python -m unittest -v \
  test_valta_verify.py \
  test_action_lifecycle.py \
  test_cross_system_proof.py
```

## Evidence delivered by the demo

- canonical action identity and digest;
- policy decision and reason code;
- durable reservation version;
- fencing generation;
- provider request and status;
- external rail credit count;
- linked customer-ledger posting count;
- justified recovery verdict;
- hash-chained lifecycle receipt;
- independent receipt-verification result;
- tamper-detection regression.

## The seven-question self-test

A team should be able to answer all seven:

1. What exact evidence binds authorization to the amount, recipient, and action?
2. Who owns the dispatch boundary after a timeout or restart?
3. How is a stale worker prevented from dispatching later?
4. What does provider `accepted` actually certify?
5. What independently proves the external economic effect?
6. What blocks retry while the effect remains unknown?
7. Can a second process reproduce the same verdict from the evidence?

Any answer of `unknown`, `manual`, or `it depends on another system` identifies a candidate recovery boundary.

## Good pilot fit

This proof becomes commercially useful when a team has:

- one bounded payment, payout, escrow, wallet, or settlement workflow;
- timeout, retry, fallback, concurrency, or restart uncertainty;
- a sandbox, simulator, test contract, test ledger, or authorized code path;
- an independently observable final state;
- a product, payments, reliability, risk, or engineering owner;
- budget for a fixed-scope verification engagement.

## Not a fit

- no authorized test surface;
- no observable final economic state;
- an unlimited audit request;
- a request for custody or production credentials;
- a demand for universal exactly-once guarantees;
- free custom implementation without a commercial scope.

## Claim boundary

This proof demonstrates a declared sandbox boundary:

```text
durable reservation
+ provider fencing enforcement
+ sandbox idempotency semantics
+ independent provider / rail / ledger observation
+ verifiable lifecycle receipt
```

It does not claim:

- universal exactly-once execution across arbitrary external systems;
- cryptographic authenticity beyond the implemented receipt integrity checks;
- custody, insurance, compliance certification, or production readiness;
- financial savings that a customer has not supplied and supported.

## One question for the reader

> Which transition in your workflow becomes impossible to prove automatically after the response disappears?

Related assets:

- [`plc-1-accepted-is-not-settled.md`](plc-1-accepted-is-not-settled.md)
- [`demo-script-90s.md`](demo-script-90s.md)
- [`plf-launch-v1.md`](plf-launch-v1.md)
- [`pilot-one-pager.md`](pilot-one-pager.md)
