# Pilot ROI and Evidence Readout

> Complete this only with customer-supported measurements and reproducible pilot evidence. Do not invent prevented loss, incident frequency, or labor cost.

## 1. Pilot identity

| Field | Value |
|---|---|
| Customer / anonymized account | |
| Workflow | |
| Pilot start / end | |
| Fixed pilot fee | |
| Test surface | sandbox / API / contract / code path / simulator |
| Policy version | |
| Scenarios executed | |

## 2. Economic boundary

Describe the exact action and the economic state that must remain correct.

```text
request
-> authority / policy
-> execution
-> final economic state
-> reconciliation / evidence
```

### Value under control

| Measurement | Customer-supported value | Evidence source |
|---|---:|---|
| Value exercised during pilot | | |
| Typical value per action | | |
| Estimated monthly workflow volume | | |
| Maximum value exposed by tested path | | |

These values describe exposure. They are not automatically counted as value protected.

## 3. Baseline cost of the problem

| Baseline measure | Before pilot | Evidence source |
|---|---:|---|
| Incidents in an agreed historical period | | |
| Duplicate / inconsistent outcomes | | |
| Mean investigation time | | |
| Mean recovery / reconciliation time | | |
| Fully loaded operator cost per hour | | |
| Refund, dispute, fee, or stranded-funds cost | | |
| Audit records inspected per incident | | |

## 4. Scenario results

| Scenario | Expected invariant | Result | Reproducible evidence | Economic relevance |
|---|---|---|---|---|
| Timeout + retry | One logical intent creates at most one effect | | | |
| Duplicate / replay | Consumed identity cannot execute again | | | |
| Stale authority / state | Old decision cannot move current value | | | |
| Conflicting action | Only one compatible economic transition wins | | | |
| False success | Dispatch cannot impersonate observed outcome | | | |

Add or remove rows to match the agreed fixed scope.

## 5. Supported pilot value

Count only values directly supported by the pilot or customer records.

```text
supported pilot value =
    confirmed duplicate / wrong economic effect prevented
  + supported manual investigation cost avoided
  + supported recovery / reconciliation cost avoided
  + supported audit-review cost avoided
```

| Component | Supported amount | Evidence / calculation |
|---|---:|---|
| Wrong or duplicate effect prevented | | |
| Investigation cost avoided | | |
| Recovery cost avoided | | |
| Audit-review cost avoided | | |
| **Total supported pilot value** | | |

```text
pilot ROI multiple = total supported pilot value / fixed pilot fee
```

If the numerator is not supportable, report `NOT ESTABLISHED` instead of a guessed ROI.

## 6. Engineering value retained

| Retained asset | Yes / No | Location / owner |
|---|---|---|
| New regression test | | |
| New invariant or policy rule | | |
| Reproducible failure trace | | |
| Permit / decision record | | |
| Execution / outcome receipt | | |
| Incident-audit procedure | | |
| CI or monitoring integration | | |

## 7. Product-quality metrics

| Metric | Result |
|---|---:|
| Unsafe injected actions executed | |
| Permit / decision verification success | |
| Evidence completeness | |
| False block rate | |
| HOLD / inconclusive rate | |
| Local decision p95 | |
| Offline verification p95 | |
| Incident reconstruction time before | |
| Incident reconstruction time after | |

## 8. Commercial verdict

Choose one:

```text
TECHNICAL_POSITIVE
- a material failure/control gap was confirmed or a valuable regression was retained

COMMERCIAL_POSITIVE
- supported value exceeded the fee or the customer requests recurring/expanded coverage

TECHNICAL_PASS_NO_CURRENT_BUYER_VALUE
- tested invariants held, but no meaningful operational or commercial value was established

INCONCLUSIVE
- the available test surface or evidence was insufficient
```

### Final recommendation

```text
STOP
ITERATE ONE MORE BOUNDED TEST
EXPAND TO ANOTHER WORKFLOW
CONVERT TO RECURRING ASSURANCE
```

### Recurring decision question

> If this control and evidence package ran continuously on this workflow, what would the team pay to retain it, and which measurable outcome would justify renewal?

## 9. Boundaries

- Exposure is not equal to prevented loss.
- A technical PASS is not automatically commercial success.
- `REJECT` and `HOLD` can create value, but only when their operational benefit is measured.
- The readout is not insurance, financial coverage, or a guarantee of future loss prevention.
