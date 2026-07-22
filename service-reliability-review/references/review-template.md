# Service Reliability Review Template

```markdown
# Service Reliability Review

## High-severity findings
1. <Finding, evidence, impact, required action>

## Verdict
<Ready | Conditional | Not ready> — <high | medium | low> confidence

<Connect the verdict to the largest failure-propagation risk and the quality of evidence.>

## Scope and targets
- Critical journeys:
- Reliability and latency objectives:
- Load/burst assumptions:
- Allowed rejection, delay, degradation, or asynchronous completion:
- Ownership and constraints:

## Failure propagation map
| Operation/dependency | Criticality | Side effect/idempotency | Deadline | Failure modes | Shared resources | User-visible effect |
| --- | --- | --- | --- | --- | --- | --- |

## Control matrix
| Operation/dependency | Policy/control | Parameters and source | Safe degradation | New cost/risk | Owner |
| --- | --- | --- | --- | --- | --- |

## Overload protection
| Scope | Constrained resource | Measurement | Algorithm | Admission behavior | Threshold evidence | Limiter failure behavior |
| --- | --- | --- | --- | --- | --- | --- |

## Observability coverage
| Control/failure | Operator question | Logs | Traces | Metrics | Alert/action | Gap |
| --- | --- | --- | --- | --- | --- | --- |

## Verification matrix
| Injected condition | Expected user behavior | Expected control transition | Required evidence | Recovery/stop condition | Result |
| --- | --- | --- | --- | --- | --- |

## Prioritized actions
1. <Action, owner, evidence required, completion condition>

## Unknowns and assumptions
- <Unknown, why it matters, how to resolve it>
```

## Finding Severity

- **Critical**: can cause incorrect irreversible business behavior, widespread outage, or unbounded resource consumption on a critical path.
- **High**: can cause cascading failure, prolonged degradation, or an invisible protection failure under credible load.
- **Medium**: weakens diagnosis, recovery, tuning, or containment but has a bounded immediate impact.
- **Low**: maintainability or clarity issue with no credible near-term reliability consequence.

Lead with findings only when supported by evidence. If a material control cannot be evaluated because targets, load, configuration, or telemetry are absent, report the evidence gap and lower confidence rather than guessing.

## Manual Walkthrough Scenarios

### Slow dependency

Verify that the end-to-end deadline is divided across attempts, the retry gate does not extend work beyond the caller's budget, isolation prevents global pool exhaustion, the circuit eventually stops waste, degradation is safe, and logs/traces/metrics show the same sequence.

### Burst plus retry amplification

Verify that admission occurs before expensive work, limiter behavior matches the protected resource, retries have a single owner and a global cap, rejected/queued/degraded outcomes are visible, and telemetry remains usable during the burst.
