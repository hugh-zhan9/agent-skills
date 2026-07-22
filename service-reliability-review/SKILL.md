---
name: service-reliability-review
description: Use when designing or reviewing runtime reliability for networked services, including deadlines, timeouts, retries, circuit breakers, isolation, degradation, rate limiting, logs, distributed traces, metrics, or whether those controls are observable and verifiable.
---

# Service Reliability Review

Review resilience, overload protection, and observability as one system. A control is incomplete until operators can see when it activates, measure its effect, distinguish protection from harm, and verify recovery.

## Required Outcome

Return one readiness verdict:

- **Ready**: critical paths have bounded failure behavior, overload protection, sufficient telemetry, and tested recovery.
- **Conditional**: the design is viable, but named gaps must be closed before the stated scope or traffic level.
- **Not ready**: an unbounded or invisible failure mode can still cause incorrect behavior, cascading failure, or uncontrolled overload.

Base the verdict on evidence and explicit unknowns, not the presence of particular products or patterns.

## Workflow

### 1. Establish reliability targets

Record:

- Critical user journeys and non-critical side paths.
- Availability, latency, correctness, throughput, and recovery objectives.
- Expected steady load, burst shape, concurrency, and known capacity limits.
- Which responses may be delayed, rejected, degraded, queued, or completed asynchronously.
- Runtime, deployment, and ownership constraints.

If targets or traffic assumptions are missing, label them as decision-blocking unknowns. Do not invent thresholds.

### 2. Map failure propagation

Trace each critical request across dependencies and resource pools. For every remote operation, record:

- Its criticality, idempotency, and side effects.
- The caller's remaining deadline and the dependency's latency distribution.
- Failure classes: explicit failure, rejection, timeout/slow response, ambiguous outcome, overload, and telemetry failure.
- Shared resources that can spread failure: threads, connections, queues, memory, CPU, network, or a common downstream dependency.
- What the caller and user observe when the operation fails.

Distinguish transient faults from persistent faults and critical-path work from optional work. Use [control-selection.md](references/control-selection.md) to choose a failure policy.

### 3. Design bounded resilience controls

For each dependency:

1. Allocate an end-to-end deadline and smaller per-attempt time budgets.
2. Allow retries only for plausibly transient failures when the operation is idempotent or has an explicit deduplication mechanism.
3. Count retry attempts across every layer. Assign one owner for the retry policy so attempts do not multiply invisibly through clients, gateways, proxies, and load balancers.
4. Add circuit breaking when repeated failures or slow calls should stop consuming resources. Define minimum traffic, trip criteria, open duration, recovery probes, and fallback behavior.
5. Isolate scarce resources so one dependency, tenant, or feature cannot exhaust the whole service. State the isolation unit and the resource cost it adds.
6. Define degradation semantics. A fallback must remain safe and recognizable; it must not convert an explicit failure into plausible but incorrect business data.

Do not add every control mechanically. Explain which failure mode each control contains and which new failure mode or cost it introduces.

### 4. Design overload protection

Choose a limit dimension that represents the constrained resource: requests, business operations, concurrent work, bytes, queue depth, or another measured unit. Then specify:

- Enforcement point and scope: edge, service, dependency, tenant, operation, or global.
- Admission policy: reject, degrade, or queue with a bounded wait.
- Algorithm and burst behavior.
- Threshold source: capacity evidence and operating margin, not a guessed constant.
- Distributed coordination cost and the limiter's own failure behavior.

Ensure rejected or queued work does not consume most of the budget before admission is decided. See [control-selection.md](references/control-selection.md) for algorithm tradeoffs.

### 5. Bind controls to observability

For every timeout, retry policy, circuit breaker, isolation pool, fallback, and limiter, define:

- **Logs** for meaningful state transitions and operator-relevant events, with correlation identifiers and no secrets.
- **Traces** that show the critical path, attempt relationships, latency allocation, errors, and degraded branches.
- **Metrics** that reveal request rate, failures, latency distribution, saturation, retry amplification, circuit state, fallback outcomes, isolation pressure, and admission decisions.
- **Alert or operator action** tied to user impact or exhaustion risk.
- **Telemetry health** so missing data is not mistaken for a healthy system.

Use [observability-contract.md](references/observability-contract.md). Reject telemetry that has no operational question or expected action.

### 6. Verify behavior under failure and load

Require reproducible tests for the material risks:

- Dependency failure, rejection, slowness, and ambiguous completion.
- Exhausted thread, connection, queue, or concurrency partitions.
- Sudden bursts and sustained overload.
- Dependency recovery and circuit transition back to normal.
- Telemetry delay, loss, or backend outage.

For each test, state the injected condition, expected user-visible behavior, control transition, telemetry evidence, recovery condition, and stop criterion. Verify that retries remain within the deadline, isolation contains the blast radius, overload produces deliberate admission decisions, and the evidence can be correlated across logs, traces, and metrics.

### 7. Produce the review

Follow [review-template.md](references/review-template.md). Lead with high-severity findings, then the verdict, control matrix, observability gaps, verification results, and prioritized next actions.

When reviewing an existing system, cite repository files, configuration, dashboards, tests, incident records, or measured data. Clearly separate observation, inference, and missing evidence. Do not implement changes unless the user also asks for implementation.

## Guardrails

- Every remote call needs a finite deadline; retry is not a substitute for timeout.
- Never retry non-idempotent or ambiguous operations without a deduplication or reconciliation design.
- Never evaluate retries one layer at a time; calculate aggregate amplification.
- Circuit breakers protect resources; they do not repair the dependency.
- Queues must be bounded and their wait must fit the caller's deadline.
- Do not treat averages as sufficient latency evidence; inspect distributions and tail behavior.
- Keep secrets, credentials, personal data, and unbounded payloads out of logs and trace attributes.
- Avoid unbounded metric label cardinality.
- Do not assume tool defaults or product semantics. Verify the pinned version and current official documentation when a decision depends on them.

## Provenance

This workflow operationalizes selected *The Fenix Project* sections documented in [source-notes.md](references/source-notes.md). It summarizes and restructures the source rather than reproducing it.
