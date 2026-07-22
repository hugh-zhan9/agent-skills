# Observability Contract

Observability is the evidence layer for reliability controls. Design it around questions and actions, not around collecting every available field.

## Start With Operator Questions

At minimum, the system should answer:

- Which user journey is failing or slowing down?
- Which dependency or resource is responsible?
- Is the fault isolated, spreading, or recovering?
- Are retries recovering requests or amplifying load?
- Is a circuit open because the dependency is unhealthy or because thresholds are wrong?
- Is degradation preserving a safe business outcome?
- Who is being rate-limited, where, and because which resource is constrained?
- Is missing telemetry caused by a healthy quiet system or a broken collection path?

Every dashboard, alert, log event, trace attribute, and metric should answer a named question or support a named action.

## Logs

Log discrete, operator-relevant events:

- Control configuration at startup or change time, excluding secrets.
- Circuit state transitions and recovery results.
- Durable fail-back handoff, exhaustion, and terminal failure.
- Degradation activation and the chosen fallback class.
- Limiter mode changes or unusual admission failures.
- Unhandled failures and recovery actions.

Use structured fields and carry a trace/correlation identifier through the request. Include service, operation, outcome, control name, reason class, and configuration revision when useful.

Avoid:

- Secrets, credentials, personal data, and complete request/response bodies.
- Fetching remote or expensive data solely to enrich a log.
- Dumping routine method arguments, return values, and durations that belong in traces or metrics.
- Error stacks for failures already handled as expected control flow.

The collection path should buffer bounded bursts and fail independently from the request path. Define acceptable delay and loss; do not make request success depend on the central log backend.

## Traces

Use traces to reconstruct the critical path and explain where time and attempts went. Propagate trace context across supported synchronous and asynchronous boundaries.

Capture, with bounded attributes:

- Service and operation identity.
- Parent/child or linked attempt relationships.
- Start time, duration, status, and error class.
- Retry attempt number and whether the attempt was original, failover, or asynchronous recovery.
- Circuit, isolation, degradation, and rate-limit decisions when they affect the path.
- Queue or admission wait where material.

Choose an instrumentation and sampling strategy with an explicit overhead budget. Ensure errors, slow traces, or rare control transitions remain diagnosable without assuming every request is stored. Do not place secrets or unbounded payloads in spans.

## Metrics

Use counters for cumulative events, gauges for current state or utilization, and histograms/summaries for distributions. Prefer dimensions with bounded cardinality such as service, operation class, outcome, dependency, region, or control state. Do not use user IDs, request IDs, raw URLs, or arbitrary error text as labels.

### Baseline service signals

- Request/admission rate and completed business-operation rate.
- Success, explicit failure, rejection, timeout, and cancellation counts.
- End-to-end and dependency latency distributions.
- Concurrency, queue depth, thread/connection utilization, CPU, memory, and other actual saturation signals.

### Control-specific signals

| Control | Minimum signals | Interpretation risk |
| --- | --- | --- |
| Timeout | Count by operation/dependency; configured budget; latency distribution | A timeout count alone cannot distinguish a slow dependency from an unrealistically short budget |
| Retry | Original requests; total attempts; attempts per request; recovered successes; terminal failures; added latency | Eventual success can hide harmful amplification |
| Circuit breaker | State; transitions; evaluated volume; failure/slow-call rate; short-circuited calls; probe outcomes | An open circuit may be correct protection or a bad threshold |
| Isolation | Capacity; in-use resources; queue depth; rejections; wait time; saturation by partition | Low global utilization can hide one exhausted partition |
| Degradation | Activations; fallback type; fallback success/failure; staleness or backlog; reconciliation outcome | A technically successful fallback may be a business failure |
| Rate limiter | Allowed, rejected, degraded, and queued work; wait time; limit and capacity inputs; results by bounded policy class | Rejections can be protection, misconfiguration, or unfair allocation |
| Telemetry pipeline | Accepted, dropped, delayed, sampled, export failures, storage/query availability | Missing evidence must not be interpreted as zero failures |

## Correlation

- Carry trace IDs into logs where supported.
- Use consistent service, operation, outcome, and dependency names across signals.
- Link a metric anomaly to representative traces and relevant state-transition logs.
- Preserve configuration or deployment revision so behavior can be compared before and after a change.

## Alerts and Actions

Alert on user impact, objective risk, or imminent resource exhaustion. Each alert needs an owner, evidence link, first diagnostic step, mitigation, and recovery condition. Avoid paging on every retry, breaker transition, or individual rejection; aggregate them into meaningful conditions while retaining events for diagnosis.

Treat dashboards and alerts as testable artifacts. During failure and load tests, verify that the expected signal appears, the alert routes correctly, and the linked evidence is sufficient to choose an action.
