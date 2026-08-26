# Verified Transition MVP v1

Status: product decision draft  
Public product name: **TBD after naming and trademark review**  
Incubation repository: `valta-pilot-lab`

## 1. Product decision

Build one sellable system for one narrow promise:

> Before a financially meaningful action executes, verify that the exact action is still authorized. After dispatch, verify the actual economic outcome. After timeout or interruption, recover without silently creating a duplicate effect. Export evidence that another party can inspect and replay.

This is a **verified-transition control and evidence layer**. It is not a wallet, payment rail, custodian, bank, general AI platform, formal-verification certificate, or production processor.

The first product is a paid assurance pilot for one workflow such as:

```text
request
  -> authorization / policy check
  -> durable reservation
  -> dispatch
  -> external observation
  -> reconciliation
  -> final evidence receipt
```

The initial commercial variants are:

1. creator payout and reconciliation;
2. escrow release, dispute, and final settlement;
3. agent-initiated vendor payment in a sandbox or test environment.

## 2. Why this is the right entry point

The portfolio already contains separate implementations for the main parts of the lifecycle:

| Repository | Reusable role in the product | MVP status |
|---|---|---|
| [`ContractGraph-QA`](https://github.com/safal207/ContractGraph-QA) | Adversarial state-transition testing, shortest failing paths, deterministic evidence bundles, retest | Revenue-ready verification surface |
| [`ProofPath`](https://github.com/safal207/ProofPath) | Pre-execution intent, authority, policy, budget, recipient, and replay checks | Reusable gateway semantics |
| [`safal207-AgentProof-AI`](https://github.com/safal207/safal207-AgentProof-AI) | Fresh authorization, action fidelity, duplicate protection, observed-outcome verification | Working deterministic demo core |
| [`Causal-Memory-Layer`](https://github.com/safal207/Causal-Memory-Layer) | Approval, task, delegation, and policy ancestry | Working audit component |
| [`T-Trace`](https://github.com/safal207/T-Trace) | Portable action receipts, deterministic replay, explicit assurance boundaries | Working protocol and benchmark |
| [`LiminalDB`](https://github.com/safal207/LiminalDB) | Durable transition lifecycle, WAL, replay, checkpoints, continuation decisions | Strong R&D substrate; integration follows a storage interface |
| [`CaPU`](https://github.com/safal207/CaPU) | Unified permission-first state machine and future execution boundary | Product architecture and future runtime |
| [`ATMAN-LATTICE`](https://github.com/safal207/ATMAN-LATTICE) | Governed drift response and forward-only remediation | Later enterprise recovery profile |
| [`COSMIC-ORGANICS`](https://github.com/safal207/COSMIC-ORGANICS) | Future sparse, verifiable hardware acceleration | Research only; not required for first revenue |

The commercial moat is not any one repository. It is the **end-to-end contract across authorization, execution, observed effect, recovery, and independently inspectable evidence**.

Do not merge all repositories into one monolith. Keep them independently testable and integrate only through small versioned contracts.

## 3. Buyer and qualifying problem

### First buyer

A CTO, head of engineering, security lead, payments lead, protocol founder, or operations owner responsible for a workflow where automation or an AI agent can trigger a financially meaningful action.

### Good first workflow

A workflow qualifies when it has all of the following:

- an action with measurable financial or operational consequence;
- a retry, concurrency, stale-state, authorization, settlement, or reconciliation risk;
- a sandbox, test contract, simulator, bounded API, or source path we are authorized to inspect;
- an owner willing to agree on explicit invariants and a paid pilot price;
- a final state that can be observed independently of the model's own claim.

### Disqualifiers

Do not accept the pilot when:

- the customer wants an unlimited security audit for a validation-pilot fee;
- there is no authorized test surface;
- there is no observable final state;
- success depends only on the AI model saying it succeeded;
- the customer requires custody, movement of real funds, or an insurance guarantee;
- the integration is mostly bespoke work with no reusable adapter or learning value.

## 4. MVP lifecycle

The current prototype records an `action_id` as consumed immediately after an `ALLOW` decision. That is sufficient for a small demonstration but unsafe as a production lifecycle: a crash after `ALLOW` and before the external effect can make the action look permanently duplicated even though nothing happened.

Replace the boolean seen/not-seen model with an explicit durable state machine:

```text
PROPOSED
   |
   v
EVALUATED
   |-- BLOCKED
   |-- INCONCLUSIVE
   `-- ALLOW
          |
          v
       RESERVED
          |
          v
      DISPATCHING
          |
          v
       DISPATCHED
          |
          v
       OBSERVING
          |-- VERIFIED
          |-- UNVERIFIED
          `-- RECONCILE_REQUIRED
                    |
                    v
                 FINALIZED
```

Additional safe terminal or recovery states:

```text
RESERVATION_EXPIRED
RELEASED_NO_EFFECT
CANCELLED_BEFORE_DISPATCH
RECONCILE_REQUIRED
MANUAL_REVIEW_REQUIRED
```

### Critical recovery rule

A timeout is not proof that no effect occurred.

```text
known no effect       -> reservation may be released under policy
known effect          -> observe, reconcile, and finalize
unknown effect        -> RECONCILE_REQUIRED; never retry blindly
```

### Claim boundary

Do not claim universal exactly-once execution. The safe claim depends on the adapter:

- **at-most-once dispatch** when a durable reservation and fencing token protect the dispatch boundary;
- **idempotent replay** when the downstream system honors a stable idempotency key;
- **duplicate-safe reconciliation** when the downstream effect can be independently observed;
- **explicit uncertainty** when none of those guarantees can be proven.

## 5. Canonical contracts

Use a small versioned protocol family. `CAUSAL-DNA` may later host these schemas, but it must not be marketed as an implemented product until the schemas and conformance tests exist.

### `TransitionRequest`

Binds:

- request and action identity;
- actor or agent identity;
- action type and exact parameters;
- target and amount;
- human intent or upstream task reference;
- policy version and authorization epoch;
- freshness evidence;
- requested idempotency semantics;
- expected external outcome.

### `DecisionReceipt`

Binds:

- `ALLOW`, `BLOCK`, or `INCONCLUSIVE`;
- stable reason code;
- canonical action digest;
- evaluated policy snapshot;
- evidence digest;
- assurance boundary and known limitations.

### `ReservationReceipt`

Binds:

- durable reservation identity;
- action digest;
- lease or expiry evidence;
- fencing token / attempt generation;
- state version;
- permitted recovery paths.

### `DispatchReceipt`

Binds:

- reservation and action digest;
- adapter and downstream request identity;
- dispatch attempt number;
- accepted/rejected/unknown transport result;
- downstream idempotency key when supported.

### `EffectObservation`

Binds:

- evidence source;
- observed final balance, status, or state;
- observation timestamp supplied as evidence;
- confidence and completeness boundary;
- relation to the expected effect.

### `FinalReceipt`

Binds:

- final verdict: `VERIFIED`, `BLOCKED`, `UNVERIFIED`, `DUPLICATE`, or `RECONCILE_REQUIRED`;
- complete receipt ancestry;
- final economic state;
- replay and independent-verification material;
- limitations and unresolved evidence.

## 6. Minimal API

```text
POST /v1/actions/evaluate
POST /v1/actions/{action_id}/reserve
POST /v1/actions/{action_id}/dispatch
POST /v1/actions/{action_id}/observe
POST /v1/actions/{action_id}/finalize
POST /v1/actions/{action_id}/release
GET  /v1/actions/{action_id}
GET  /v1/actions/{action_id}/receipt
POST /v1/receipts/verify
```

Every mutating endpoint requires an expected state version or fencing token. A stale caller must fail closed instead of overwriting a newer lifecycle state.

## 7. MVP invariants

1. **The model proposes; it never authorizes itself.**
2. **Authorization is bound to the exact canonical action digest.**
3. **Policy and authorization freshness are checked from explicit evidence, not hidden wall-clock reads inside deterministic projection logic.**
4. **A durable reservation is established before dispatch.**
5. **An `ALLOW` decision is not an execution receipt.**
6. **Provider acceptance is not the final economic outcome.**
7. **Unknown outcome is never silently converted to success or safe retry.**
8. **Concurrent attempts cannot both own the same active fencing generation.**
9. **The supported adapter cannot produce two finalized effects for one action identity within its declared guarantee boundary.**
10. **Every final verdict is reproducible from the exported evidence or explicitly marked as externally unverifiable.**
11. **A failed proof or incomplete evidence returns `INCONCLUSIVE` / `RECONCILE_REQUIRED`, not a safety claim.**
12. **Recovery creates a new traceable state; it does not rewrite prior evidence.**

## 8. Thin vertical slice

Build one end-to-end sandbox workflow before adding more integrations:

```text
AI/model proposes vendor payout
  -> exact request is evaluated
  -> action is durably reserved
  -> sandbox payout adapter dispatches
  -> observer checks the sandbox ledger
  -> final receipt is exported
  -> verifier reconstructs the verdict
```

Required scenarios:

1. valid action and verified settlement;
2. stale authorization blocked before reservation;
3. action changed after authorization;
4. duplicate and concurrent retries;
5. provider accepted but ledger did not change;
6. process crash after reservation but before dispatch;
7. timeout after dispatch with unknown outcome;
8. recovery after restart without a second economic effect.

The LLM may produce the proposal, but all business-critical verdicts remain deterministic.

## 9. Implementation strategy

### Storage

Define an `ActionStore` interface first.

Use a transactional local adapter for the first vertical slice so the lifecycle can be shipped and tested quickly. Keep the contract compatible with a later LiminalDB adapter. Do not block first revenue on a full cross-repository database integration.

Required store primitives:

```text
create_proposal
record_decision
reserve_if_version_matches
mark_dispatch_started
record_dispatch_result
record_observation
finalize_if_version_matches
release_if_safe
load_history
```

Every transition must be atomic with respect to action identity and expected state version.

### Evidence

- CML-compatible ancestry for task, approval, delegation, and policy lineage;
- T-Trace-compatible state-transition records and replay package;
- AgentProof-style outcome grounding and receipt verdicts;
- ContractGraph-QA scenarios for adversarial lifecycle testing;
- external signatures or anchoring added only after the unsigned deterministic contract is stable.

### Packaging

The first distribution should contain:

- Docker image;
- local CLI and HTTP API;
- one sandbox payout adapter;
- one deterministic observer;
- one-command demo;
- evidence-bundle verifier;
- customer pilot worksheet;
- ROI readout template;
- explicit non-claims.

## 10. Commercial model

### Stage 1 — founding validation pilot

Use only for the first one to three design partners.

```text
Price: USD 750
Scope: one bounded workflow, three to five scenarios
Delivery cap: no more than eight focused engineering hours unless repriced
Access: sandbox, simulator, test contract, or bounded repository path
Payment: fixed fee; no free pilot
```

This price is profitable only when the adapter is already available or reusable and the delivery time is strictly capped.

### Stage 2 — standard assurance pilot

```text
Price hypothesis: USD 2,500–5,000
Scope: one workflow, five to eight failure/recovery scenarios
Deliverables: integration adapter, executable invariants, evidence bundle, regression pack, ROI readout
```

### Stage 3 — production integration

```text
Price hypothesis: USD 10,000–30,000
Scope: production-relevant adapter, durable deployment, observability, runbooks, load/failure testing, security review support
```

### Stage 4 — recurring assurance

Use a hybrid model only after a pilot proves recurring value:

```text
base platform / support fee
+ usage band for governed transitions
+ optional release/retest package
```

Do not price recurring value as a percentage of hypothetical catastrophic loss. Report confirmed prevented loss, supported operational savings, and expected protected value separately.

### Later — hardware and OEM

CaPU/CMC and COSMIC become a separate business only after software usage identifies a repeated high-volume boundary worth moving closer to hardware.

Possible later economics:

```text
non-recurring engineering fee
+ annual IP license
+ per-device or per-chip royalty
+ certification / conformance suite
```

No fabrication plant is required. The long-term hardware route is fabless: software semantics -> FPGA proof -> board measurements -> licensed IP block -> foundry partner.

## 11. Unit-economics rules

Track for every engagement:

- cash price paid;
- delivery hours;
- reusable versus customer-specific code;
- customer integration hours;
- money under control;
- confirmed prevented loss;
- supported operational savings;
- unresolved risk and evidence limitations;
- recurring or expansion willingness.

Targets:

- founding pilot: hard delivery cap and positive cash contribution;
- standard pilot: at least 70% gross-margin target after repeatable adapters exist;
- no unpaid custom integration;
- no unsupported ROI multiple;
- no investor claim of validated economics before at least three paid production-relevant pilots and one recurring or expansion signal.

## 12. Go-to-market

### Opening question

Use a concrete failure boundary, not an abstract platform pitch:

> If your payment or settlement provider accepts a request, your application times out, and the same agent retries, can your team prove whether zero, one, or two economic effects occurred — and recover safely without guessing?

### Initial target accounts

- agentic-payment and wallet infrastructure teams;
- payout and creator-economy platforms;
- escrow and settlement protocols;
- marketplaces with automated refund/reversal flows;
- teams allowing agents to call paid APIs or purchase services;
- smart-contract teams with time, retry, dispute, or finalization boundaries.

### Sales sequence

```text
one sharp question
  -> one bounded failure hypothesis
  -> async technical exchange
  -> fixed-scope paid pilot
  -> evidence and ROI readout
  -> recurring assurance decision
```

Keep the sales channel asynchronous and evidence-first. Do not require a live meeting to qualify or deliver the first pilot.

## 13. Thirty-day execution plan

### Week 1 — correct lifecycle semantics

- replace the in-memory seen-ID set with explicit states;
- implement transactional reservation, fencing generation, finalize, safe release, and restart recovery;
- add negative tests for every crash boundary;
- add concurrent retry tests;
- preserve deterministic, evidence-supplied time semantics.

### Week 2 — ship one vertical slice

- implement the sandbox payout adapter;
- implement an independent ledger observer;
- export a portable receipt bundle;
- add one-command Docker demo;
- verify replay after process restart.

### Week 3 — turn it into a pilot product

- bind the lifecycle to ContractGraph-QA scenarios;
- finalize the customer worksheet and authorization boundary;
- update the 90-second demo and one-pager;
- produce one sample evidence bundle and one concise ROI readout;
- run a clean-checkout verification path.

### Week 4 — prove willingness to pay

- contact a focused list of qualified teams using the opening question;
- offer the founding pilot only where the workflow is bounded and observable;
- close and deliver the first paid pilot;
- record price, delivery cost, protected value, and expansion decision;
- stop or narrow features that do not contribute to a paid result.

## 14. Decision gates

### Continue

Continue toward a recurring product when:

- at least three customers pay for comparable production-relevant pilots;
- at least one customer requests recurring coverage or a second workflow;
- adapters are becoming reusable;
- evidence reduces investigation, reconciliation, or regression effort;
- standard-pilot delivery can meet the margin target.

### Narrow

Narrow to a high-value independent QA service when customers pay for findings and regression evidence but do not want an always-on runtime.

### Stop or reposition

Reposition when repeated qualified prospects agree the failure is real but will not pay, integration costs exceed supported value, the final outcome cannot be observed, or existing controls fully satisfy the need.

## 15. Non-goals for v1

- custody or movement of real customer funds;
- replacement of payment rails, wallets, IAM, observability, or formal verification;
- universal exactly-once guarantees;
- universal causal truth;
- autonomous policy creation by an LLM;
- enterprise compliance certification;
- production distributed consensus;
- production FPGA or ASIC;
- claims about consciousness, metaphysics, quantum advantage, or biological computation.

## 16. Immediate next implementation issue

The first engineering issue should be:

> Replace `ActionLedger` seen-ID semantics with a durable reservation, observation, finalization, and recovery lifecycle, including crash and concurrent-retry tests.

Nothing else should block that task. It is the seam between a convincing demo and a financial control product.
