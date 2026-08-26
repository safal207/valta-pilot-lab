# Prototype 001 — verified action lifecycle

A deterministic policy evaluator plus a durable local lifecycle for financially meaningful AI actions.

## Core separation

```text
policy decision
  != durable reservation
  != dispatch result
  != observed economic effect
  != final verdict
```

`verify_action` returns `ALLOW`, `BLOCK`, or `INCONCLUSIVE`. An `ALLOW` response does **not** consume the action identity and does not claim that execution occurred.

`action_lifecycle.py` provides the explicit state transitions required after evaluation:

```text
EVALUATED
  -> RESERVED
  -> DISPATCHING
  -> DISPATCHED
  -> OBSERVING
  -> VERIFIED | UNVERIFIED | RECONCILE_REQUIRED
  -> FINALIZED
```

Known-no-effect evidence may release a reservation. An unknown post-dispatch outcome moves to `RECONCILE_REQUIRED`; it is never converted into a blind retry.

## Decision contract

Input binds:

- actor / agent identity;
- proposed action and target;
- economic amount;
- policy version;
- unique action identity;
- explicit freshness evidence (`checked_at`, optional `authorization_expires_at`).

Output returns:

- verdict and stable reason code;
- policy version;
- canonical action digest;
- deterministic evidence reference;
- execution boundary (`EXECUTION_OBSERVED` or `EXTERNAL_UNVERIFIED`).

The action digest excludes evaluation time but binds the immutable action and authorization-relevant fields. Reusing an `action_id` for a changed amount, target, actor, action, policy version, or authorization envelope fails closed.

## Durable MVP store

`SQLiteActionStore` uses:

- SQLite transactions with `BEGIN IMMEDIATE`;
- expected-version compare-and-swap semantics;
- monotonically increasing fencing generations;
- separate decision, dispatch, observation, and finalization evidence;
- restart-safe materialized state;
- hash-linked lifecycle events;
- portable receipts that can be verified without the originating database.

All decision and lifecycle times are supplied as explicit evidence. Deterministic evaluation and replay never read the wall clock.

## Run

From this directory:

```bash
python -m unittest -v test_valta_verify.py test_action_lifecycle.py
python demo.py
python lifecycle_demo.py
```

With MCP dependencies installed:

```bash
python -m unittest discover -s . -p "test_*.py" -v
```

## Covered failure boundaries

- allowed and policy-blocked actions;
- stale authorization;
- evaluation does not consume identity;
- concurrent reservation race: one owner only;
- crash after `ALLOW` but before reservation;
- crash after reservation but before dispatch;
- provider acceptance without observed settlement;
- timeout after dispatch with unknown outcome;
- safe release only with known-no-effect evidence;
- stale fencing generation;
- changed action under the same identity;
- restart reconstruction;
- receipt and event-chain tampering;
- no second reservation after finalization.

## Guarantee boundary

This prototype demonstrates local durable reservation, fencing, deterministic replay, and explicit effect observation.

It does **not** claim universal exactly-once execution. End-to-end guarantees still depend on the downstream adapter's idempotency behavior, authoritative observation source, and evidence completeness. It does not hold keys, move real funds, replace a payment rail, or certify a production system.
