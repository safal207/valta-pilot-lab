# PLC 2 — Recover Without Paying Twice

Target release: 2026-09-04  
Stage: Prelaunch Content 2 — Transformation  
Primary format: short email plus executable demo link

## Subject

```text
A retry is not safe just because it is identical
```

## Email

Hi {{name/team}},

A common answer to ambiguous payment recovery is:

> “We use the same idempotency key, so the retry is safe.”

That can be an important control. It is not the whole proof.

An idempotency key may protect one API boundary while leaving other questions open:

- Did the key reach the downstream processor or rail?
- Does a fallback provider share the same key semantics?
- Can a worker that woke up after a restart still dispatch with stale authority?
- Did the provider accept the request but fail to produce the expected economic result?
- Is a delayed webhook evidence of no effect, or simply delayed evidence?

The transformation is to stop treating retry as one operation and model the complete transition:

```text
EVALUATE
  -> RESERVE
  -> DISPATCH
  -> OBSERVE
  -> RECONCILE
  -> FINALIZE
```

Each state answers a different question:

```text
EVALUATE   Was this exact action allowed?
RESERVE    Which attempt owns the right to dispatch?
DISPATCH   What request crossed the external boundary?
OBSERVE    What economic effect can be independently seen?
RECONCILE  What remains unknown or conflicting?
FINALIZE   What verdict is justified by the evidence?
```

The practical result is not “timeouts disappear.”

It is this:

```text
known no effect  -> release safely under policy
known effect     -> observe and finalize
unknown effect   -> stop blind retry and reconcile
```

In the current executable prototype, a concurrent retry test produces:

```text
24 attempts
1 reservation owner
23 stale or duplicate attempts rejected
```

The same lifecycle also distinguishes:

- provider accepted + observed final effect → `VERIFIED`;
- provider accepted + expected effect absent → `UNVERIFIED`;
- response lost after dispatch → `RECONCILE_REQUIRED`.

That last state is not a failure of the model. It is the honest answer when evidence is incomplete.

### Five-minute failure-injection checklist

Take one payment flow and ask:

1. Kill the process immediately after authorization. Can another attempt proceed safely?
2. Kill it immediately after reservation. Can ownership be recovered without creating two owners?
3. Lose the provider response after dispatch. Does the system retry or reconcile?
4. Delay or duplicate the webhook. Does local state become false success?
5. Wake an old worker after a new attempt begins. Can it still cross the dispatch boundary?

**Send me one anonymized transition from your flow. I will reply with the first invariant I would pressure-test.**

Alexey Safonov

## Demo evidence to attach or link only when ready

The public demo should show, in one command:

```text
scenario: timeout_after_dispatch
attempts: 24
reservation_owners: 1
economic_effects: 0 | 1 | unknown
verdict: VERIFIED | UNVERIFIED | RECONCILE_REQUIRED
receipt_integrity: PASS
```

Do not publish a placeholder result. Link the demo only after it runs from a clean checkout and the output is preserved.

## Reply handling

### “We already have exactly-once”

```text
That is strong if it holds end to end. What is the declared boundary: one API service, one processor, or the final economic rail?

After a response is lost post-dispatch, which evidence proves the effect count and fences a stale caller?
```

### “We use webhooks”

```text
How do you classify the state while the webhook is missing, duplicated, delayed, or out of order? Is retry blocked until an authoritative observation arrives?
```

### “We reconcile manually”

```text
That is the cost boundary I am studying. Roughly which team owns it, how often does it occur, and what evidence do they assemble before deciding whether to retry?
```
