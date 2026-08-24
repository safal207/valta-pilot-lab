# Prototypes

Implementation experiments live here.

The first prototype should be intentionally small and should prove the control/evidence contract before adding broad product features.

## Prototype 001 — verify action

Input:

- actor / agent identity;
- proposed action;
- target;
- amount or economic scope where relevant;
- policy context;
- action identity / nonce.

Output:

- `ALLOW`, `BLOCK`, or `INCONCLUSIVE`;
- reason code;
- policy/version reference;
- evidence reference;
- whether downstream execution has actually been observed or remains external/unverified.

## Non-goals for the first prototype

- production custody;
- real wallet keys;
- autonomous fund movement;
- broad dashboard/UI;
- marketplace implementation;
- invented ROI claims.

The prototype exists to make one economic-control workflow demonstrable and testable.
