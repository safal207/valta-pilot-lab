# Prototype 001 — verified action lifecycle

A deterministic control and evidence loop for an AI-driven financial action.

## Safety contract

The model may propose an action. It does not authorize itself and it does not prove that an external effect happened.

```text
EVALUATE
  -> RESERVE
  -> DISPATCHING
  -> DISPATCHED
  -> OBSERVE
  -> VERIFIED | UNVERIFIED | RECONCILE_REQUIRED
  -> FINALIZE
```

`verify_action(...) == ALLOW` records an `EVALUATED` decision only. It **does not consume the action ID**. Before dispatch, a caller must atomically call `reserve_if_version_matches(...)` and use the returned generation/fencing token.

## Durable store

`ActionLedger` is now a compatibility name for `SQLiteActionStore`; it is no longer an in-memory seen-ID set.

```python
store = ActionLedger(db_path="./data/actions.sqlite3")
```

The SQLite adapter provides:

- durable action state and append-only transition events;
- optimistic state versions;
- monotonically increasing fencing generations;
- one active reservation owner;
- restart reconstruction;
- safe pre-dispatch release only with explicit no-effect evidence;
- `RECONCILE_REQUIRED` for unknown post-dispatch outcomes;
- deterministic receipt export and hash-chain verification.

The MCP wrapper remains evaluation-only. Set `VALTA_ACTION_DB` when embedding the store in a long-running service; an unset value may use an in-memory prototype store.

## Determinism rule

No policy or lifecycle transition reads the wall clock. Freshness, reservation expiry, dispatch time, observation time, and recovery time are supplied as explicit evidence. Replaying the same evidence yields the same decision and receipt.

## Core invariants

1. `ALLOW` is not execution.
2. An action ID is bound to one canonical action digest.
3. Dispatch requires a durable reservation and current fencing generation.
4. A stale version or generation cannot overwrite a newer attempt.
5. Provider acceptance is not the final economic outcome.
6. Timeout is not proof of no effect and never enables blind retry.
7. Restart during an uncertain dispatch enters `RECONCILE_REQUIRED`.
8. Recovery appends evidence; it never rewrites prior history.

## Run

From this directory:

```bash
python -m unittest -v test_valta_verify.py test_action_lifecycle.py
python demo.py
```

With MCP dependencies installed:

```bash
python -m unittest discover -p "test_*.py" -v
```

## Covered scenarios

- normal reserve → dispatch → observe → finalize;
- policy block and stale authorization;
- repeated evaluation without false duplicate consumption;
- action-ID rebinding rejection;
- two concurrent reservations with one owner;
- crash after evaluation and after reservation;
- crash while dispatching;
- provider accepted but final state absent;
- timeout with unknown effect;
- safe release and a later fenced retry;
- stale writer rejection;
- restart reconstruction;
- deterministic receipt replay and tamper detection;
- no second finalized effect inside the declared store/adapter boundary.

## Claim boundary

This prototype does **not** claim universal exactly-once execution. Its guarantees are bounded by:

- the durable reservation store;
- the fencing token being enforced at the dispatch boundary;
- downstream idempotency support, when available;
- the completeness and independence of effect observation.

It is not a wallet, payment rail, custodian, formal-verification certificate, or production distributed consensus system.
