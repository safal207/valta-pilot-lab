# 90-Second Demo Script — From Proposed Action to Reproducible Evidence

## Goal

Show that Valta does not merely log an action. It binds the exact request to authority and policy, blocks stale or repeated execution, and keeps authorization separate from the observed outcome.

The demonstration can use the existing deterministic `verify_action` prototype or an equivalent pilot adapter.

## 0–10 seconds — The problem

**Narration**

> An automated system can request a payout or settlement in milliseconds. The expensive question comes later: was this exact action authorized under the current policy, did it execute only once, and did the downstream system actually reach the claimed result?

**Screen**

```text
Proposed action: release payout_42 for USD 5,000
```

## 10–30 seconds — A valid request

Show the bound request:

```text
action_id: payout_42-attempt_1
actor: payout_agent
operation: release_payout
target: creator_218
amount: USD 5,000
policy: payout-policy-v7
checked_at: T1
authorization_expires_at: T2
```

Run verification.

**Expected result**

```text
ALLOW
reason: POLICY_OK
evidence_ref: sha256:...
execution_boundary: EXTERNAL_UNVERIFIED
```

**Narration**

> Valta can allow the request, but it does not pretend that authorization proves the external payout succeeded.

## 30–52 seconds — Retry or replay

Submit the same logical action again with the same action identity or consumed permit.

**Expected result**

```text
BLOCK
reason: DUPLICATE_OR_REPLAY
```

**Narration**

> The second request cannot create a second economic effect just because the caller timed out or retried.

## 52–69 seconds — State changed after approval

Advance the policy epoch, change the escrow state, or expire the authorization and submit the earlier approval.

**Expected result**

```text
BLOCK
reason: STALE_AUTHORIZATION
```

**Narration**

> A previously valid decision cannot silently authorize an action after the state or policy changed.

## 69–82 seconds — False success boundary

Show a request that was authorized and dispatched, but whose downstream execution is missing or failed.

**Expected result**

```text
Decision: ALLOW
Outcome: INCONCLUSIVE or FAILED
Terminal success: false
```

**Narration**

> Dispatch is not success. The final claim remains unproven until the executor or observer provides outcome evidence.

## 82–90 seconds — Commercial close

Show the evidence bundle and the fixed pilot scope.

**Narration**

> The pilot applies this control to one real workflow, pressure-tests its highest-cost failure paths, and returns reproducible traces, regression coverage, and a supported ROI readout. One workflow, fixed scope, clear evidence.

## Demo success criteria

- normal valid request is allowed;
- duplicate/replay is blocked;
- stale authorization is blocked;
- authorization never impersonates outcome evidence;
- the same input and policy snapshot produce the same decision;
- every verdict includes a stable reason code and evidence reference.

## What not to say

Do not claim:

- exactly-once execution without durable consume/recovery semantics;
- cryptographic authenticity unless signatures are actually implemented;
- prevented-loss values without customer evidence;
- absolute safety or financial coverage;
- that the prototype is already a production control plane.
