# Ambiguous Payment Recovery Self-Test

Status: public lead magnet  
Audience: payment, payout, escrow, wallet, settlement, reliability, and agentic-commerce teams  
Input boundary: no production credentials or confidential transaction data

## Purpose

Identify the exact transition where evidence stops being sufficient for safe retry, finalization, or automated recovery.

This is a diagnostic, not a certification.

## Scoring

For every question:

```text
0 = Yes, with reproducible evidence.
1 = Partly, manually, or only inside one system.
2 = No, unknown, or not tested.
```

## Questions

| # | Question | Score | Evidence / owner |
|---:|---|---:|---|
| 1 | Is authorization bound to the exact amount, recipient, target, and action? |  |  |
| 2 | Is one execution owner durably reserved before dispatch? |  |  |
| 3 | Can an old worker be fenced after a timeout or restart? |  |  |
| 4 | Is provider `accepted` kept separate from settlement finality? |  |  |
| 5 | Can the external economic effect be observed independently? |  |  |
| 6 | Does an unknown outcome block blind retry? |  |  |
| 7 | Can another process replay the evidence and reach the same verdict? |  |  |

Maximum score: **14**.

## Interpretation

| Score | Interpretation | Next step |
|---:|---|---|
| 0–3 | The declared boundary is comparatively well defined. | Pressure-test crash, concurrency, stale-worker, and false-success paths. |
| 4–8 | Cross-system coverage is partial. | Identify manual handoffs and assumptions that are not represented as evidence. |
| 9–14 | The workflow is a high-value recovery candidate. | Map the transition and block retry until `VERIFIED`, `SAFE_TO_RETRY`, or explicit reconciliation. |

A low score is not a production guarantee. It means the team can name more of the evidence required for the declared boundary.

## Evidence inventory

```text
Authorization evidence:
Reservation / owner evidence:
Provider evidence:
External rail / recipient evidence:
Customer-ledger evidence:
Recovery owner/team:
Manual reconciliation frequency:
Median investigation time:
Value blocked while unresolved:
```

## Required one-sentence output

> The transition that becomes unknown is **[transition]**, and today the recovery decision is owned by **[team/system]**.

## Safe response model

```text
VERIFIED
One matching external effect and linked ledger result are observed.

SAFE_TO_RETRY
A pre-effect rejection and zero external effects are proven.

UNVERIFIED
Provider acceptance exists, but the expected effect is absent.

RECONCILE_REQUIRED
An effect may have occurred or evidence domains disagree.
```

## Non-claims

This self-test does not certify:

- security;
- accounting correctness;
- regulatory compliance;
- universal exactly-once execution;
- authenticity of evidence sources it cannot access;
- prevented loss or financial ROI.

Do not submit credentials, wallet keys, customer records, private transaction data, or non-public production evidence.

## Related assets

- [`proof-card-cross-system-payment.md`](proof-card-cross-system-payment.md)
- [`plc-1-accepted-is-not-settled.md`](plc-1-accepted-is-not-settled.md)
- [`demo-script-90s.md`](demo-script-90s.md)
- [`../site/index.html`](../site/index.html)
