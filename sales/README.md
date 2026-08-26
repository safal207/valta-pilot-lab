# Buyer-Ready Pilot Kit

This folder turns the verified-transition model into a small, evidence-first customer package.

## Acquisition and partner assets

- [`ambiguous-payment-recovery-self-test.md`](ambiguous-payment-recovery-self-test.md) — the public seven-question diagnostic and evidence inventory.
- [`jv-partner-kit.md`](jv-partner-kit.md) — partner selection, ready-to-publish copy, attribution links, consent boundary, referral economics, and reporting.
- [`opt-in-welcome-sequence.md`](opt-in-welcome-sequence.md) — Day 0 delivery plus three educational follow-ups for explicit opt-ins.
- [`manual-double-opt-in-operations.md`](manual-double-opt-in-operations.md) — the active Gmail + private-registry bridge: request intake, second confirmation, sequence cap, unsubscribe, deletion, and future-backend migration rules.
- [`../site/`](../site/) — the deployable privacy-conscious opt-in page, resource page, downloads, provider-neutral form adapter, and GitHub Pages workflow.

The canonical public destination is:

- **https://ambiguous-payment-recovery-kit.lovable.app/**

## Prelaunch assets

- [`plf-launch-v1.md`](plf-launch-v1.md) — the canonical Pre-Prelaunch → Prelaunch Content → paid-launch operating plan.
- [`plc-1-accepted-is-not-settled.md`](plc-1-accepted-is-not-settled.md) — PLC 1 opportunity lesson, email-ready version, public article version, self-test, send gate, and non-claims.
- [`proof-card-cross-system-payment.md`](proof-card-cross-system-payment.md) — one-page technical proof card covering provider, external rail, customer ledger, verdicts, commands, evidence, and claim boundary.
- [`demo-script-90s.md`](demo-script-90s.md) — the 90-second provider → rail → ledger demonstration aligned with the executable cross-system proof.

## Commercial assets

- [`pilot-one-pager.md`](pilot-one-pager.md) — the first commercial document to send when a qualified owner asks what the bounded pilot includes.
- [`sample-assurance-bundle.json`](sample-assurance-bundle.json) — an illustrative machine-readable request, decision, and outcome bundle.
- [`roi-readout-template.md`](roi-readout-template.md) — the commercial evidence sheet completed at the end of a pilot.

## Recommended sequence

```text
one painful question or partner mention
→ voluntary resource request
→ second explicit confirmation
→ self-test + proof card
→ PLC 1: accepted is not settled
→ PLC 2: idempotency is not recovery
→ PLC 3: five-scenario ownership experience
→ exact workflow and test-surface qualification
→ fixed-scope paid pilot
→ ROI / evidence readout
→ recurring-control decision
```

Do not send the complete prelaunch or launch sequence to an unresponsive cold address.

## Current proof message

```text
A provider can prove its own state.
The hard part is proving one economic outcome across the provider,
external rail, recipient, and customer ledger before retrying.
```

The executable demo distinguishes:

```text
VERIFIED
SAFE_TO_RETRY
UNVERIFIED
RECONCILE_REQUIRED
```

The headline concurrency scenario produces:

```text
24 attempts
1 durable reservation owner
23 stale or duplicate attempts rejected
1 external rail effect
1 linked customer-ledger posting
receipt verification: PASS
```

## What may be tailored

For each prospect, change only:

1. the exact workflow;
2. the external systems and evidence domains involved;
3. the expensive uncertainty after timeout or restart;
4. the fixed scenarios;
5. the price and delivery window after qualification;
6. the ROI metric supported by the customer’s own data.

For each distribution partner, change only:

1. the audience-specific opening;
2. the partner slug and UTM source;
3. the channel format;
4. the co-authored example, when applicable.

## Invariants that must not be weakened

- A decision for action A cannot authorize action B.
- A stale or replayed approval cannot move value.
- Authorization does not prove successful execution.
- One current fencing generation owns the dispatch boundary.
- Provider acceptance does not prove settlement finality.
- A downstream claim of success requires observed outcome evidence.
- Unknown post-dispatch outcome blocks blind retry.
- Missing or conflicting evidence is surfaced, not silently converted into success.
- Prevented-loss and ROI numbers are never invented.
- Partners do not transfer mailing lists; readers opt in directly.
- A resource request is not a confirmed subscription.
- Subscriber identities are not shared without explicit consent.
- Day 0 may be followed by no more than three educational emails.
- Any stop, unsubscribe, bounce, or deletion request suppresses future sending immediately.

## Public-repository boundary

Keep customer names, credentials, non-public architecture, transaction data, private correspondence, subscriber data, and production evidence out of this repository.

Public samples and proof bundles are illustrative sandbox evidence. They are not production signatures, attestations, insurance promises, compliance certificates, or guarantees of absolute safety.
