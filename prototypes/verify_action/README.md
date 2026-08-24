# Prototype 001 — `verify_action`

Small deterministic control/evidence loop for an AI-driven financial action.

## Contract

Input binds:

- actor / agent identity;
- proposed action;
- target;
- economic amount;
- policy version;
- unique action identity;
- explicit freshness evidence (`checked_at`, optional `authorization_expires_at`).

Output returns:

- `ALLOW`, `BLOCK`, or `INCONCLUSIVE`;
- stable reason code;
- policy version;
- deterministic SHA-256 evidence reference;
- execution boundary (`EXECUTION_OBSERVED` or `EXTERNAL_UNVERIFIED`).

## Determinism rule

`verify_action` never reads the wall clock. Freshness is derived from timestamps supplied in the evidence. Replaying the same request + policy snapshot yields the same policy decision.

## Run

From this directory:

```bash
python -m unittest -v test_valta_verify.py
python demo.py
```

## Prototype scenarios

1. Normal allowed action.
2. Policy-violating action blocked.
3. Duplicate/retry detected by `action_id`.
4. Stale authorization rejected.
5. A policy decision never claims downstream execution was verified when it was not observed.

## Boundary

The in-memory `ActionLedger` is intentionally not production durability. A paid-pilot implementation must replace it with durable storage and explicitly define reserve/consume/recovery semantics before making exactly-once claims.
