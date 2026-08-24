# Pilot Success Metrics

## Commercial success

A pilot is commercially successful when it produces evidence that the customer values the outcome enough to continue, expand, or repeat.

Track:

- pilot price paid;
- customer integration effort;
- delivery effort;
- customer willingness to continue;
- expected recurring price;
- expected gross margin.

## Economic success

Track only values that can be explained and defended.

### Money under control

Economic value associated with governed or observed actions during the pilot.

### Confirmed prevented loss

Value of invalid economic actions that were actually blocked, de-duplicated, reversed safely, or otherwise prevented.

### Expected protected value

For risks that did not occur during the pilot, use expected value only when probability and impact assumptions are explicit:

```text
expected protected value = estimated incident probability x estimated incident cost x attributable risk reduction
```

Do not mix expected protected value with confirmed prevented loss without labeling them separately.

### Operational savings

```text
operational savings = hours avoided x loaded hourly cost
```

Examples: reconciliation, approval handling, incident investigation, refund correction, and manual audit preparation.

### ROI multiple

```text
ROI multiple = (confirmed prevented loss + supported operational savings) / pilot cost
```

Expected protected value may be shown separately as an upside scenario.

## Technical success

- agreed invariants are executable or observable;
- every final verdict is tied to evidence;
- retry/concurrency behavior is reproducible;
- authorization is bound to the intended action where required;
- final economic state can be reconciled;
- ambiguous outcomes are surfaced rather than silently treated as success.

## Evidence quality

For every claimed outcome capture:

- action/request identifier;
- policy/authorization context;
- relevant timestamps or sequence ordering;
- execution result;
- final economic state;
- retry/duplicate context;
- evidence source;
- confidence / known limitations.

## Investor-readiness threshold

Do not call the economic model validated until there are at least 3 paid, production-relevant pilots with comparable measurements and at least one recurring/expansion signal.
