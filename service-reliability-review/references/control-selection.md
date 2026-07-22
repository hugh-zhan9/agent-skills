# Reliability Control Selection

Select controls from the failure semantics and time/resource budget. Do not start from a preferred library or pattern.

## Failure Policy

| Policy | Use when | Required conditions | Main risk |
| --- | --- | --- | --- |
| Fail over | Another healthy replica may complete critical work | Operation is safe to repeat and enough deadline remains | Added latency and load can worsen an outage |
| Fail fast | Repeating is unsafe or unlikely to help | Caller can handle an explicit failure | Unhandled failure can propagate upstream |
| Fail safe | Optional side work may fail without invalidating the main result | Fallback semantics are explicitly safe | Silent loss of audit, notification, or other side effects |
| Fail silent | A persistently bad dependency must stop receiving work temporarily | Recovery probing and visibility exist | Protected dependency remains unavailable during isolation |
| Fail back | Work can complete later | Durable handoff, idempotency/deduplication, retry cap, and reconciliation exist | Backlog growth and delayed permanent failure |
| Parallel call | The earliest successful result is worth duplicated work | Duplicate side effects are impossible and resource cost is justified | Load multiplication and wasted work |
| Broadcast | Every target must receive the operation | Partial completion and repair are defined | Success probability falls as targets increase |

## Timeouts and Deadlines

- Start with the user-visible end-to-end deadline.
- Reserve time for upstream handling, network overhead, fallback, and the response path.
- Give each attempt a finite budget smaller than the remaining deadline.
- Propagate cancellation or deadline information where the protocol supports it.
- Treat timeout as an ambiguous result when the remote side may have committed a side effect.
- A longer timeout consumes resources longer; a shorter timeout may create false failures. Justify it with measured latency and the service objective.

## Retry Gate

Retry only when all are true:

1. The error is plausibly transient.
2. The operation is idempotent or protected by a stable deduplication key.
3. Another attempt can finish within the remaining deadline.
4. The additional load is safe during the suspected failure.
5. Attempts and termination conditions are explicit.

Inventory attempts at every client, SDK, gateway, proxy, load balancer, worker, and asynchronous recovery loop. The worst-case call amplification is the product of the attempts configured at nested layers. Centralize ownership or disable redundant layers. Honor server backoff guidance when supported.

Track retry attempts, original requests, eventual outcomes, recovered successes, and added latency separately. A higher success count is not sufficient if retries amplify load or violate the caller's deadline.

## Circuit Breaker

Define:

- Which operation or dependency the breaker protects.
- What counts as failure: error, rejection, timeout, slow call, or a selected subset.
- Minimum observation volume and evaluation window.
- Trip threshold and the behavior while open.
- Recovery delay, probe volume, and close/reopen conditions.
- Fallback semantics and whether the caller can distinguish degraded output.

Observe transitions among normal, open, and recovery-probe states. A breaker without a recovery path or state-transition telemetry creates a hidden outage.

## Isolation

Choose the smallest resource partition that contains the intended blast radius:

- Per dependency or operation.
- Critical versus optional path.
- Tenant, customer tier, region, or workload class.
- Thread, connection, concurrency permit, queue, process, instance, or pool.

Dedicated pools improve containment but add memory, scheduling, queueing, and configuration cost. Lightweight concurrency permits reduce overhead but may not provide interruption or queue isolation. Match the mechanism to the runtime and verify the resource that actually saturates.

## Degradation

For each fallback, specify:

- Whether the output is cached, partial, stale, defaulted, queued, or explicitly unavailable.
- Maximum acceptable staleness and affected invariants.
- How clients and operators know degradation occurred.
- Whether later reconciliation is required.
- When normal behavior resumes.

Never return a type-correct default that is semantically wrong for the business operation.

## Traffic Control

### Select the measurement

Transactions, external requests, internal queries, bytes, concurrency, and queue depth describe different pressure. Select the measurement closest to the bottleneck and explain how it maps to user work.

### Select the algorithm

| Algorithm | Useful when | Burst behavior | Limitation |
| --- | --- | --- | --- |
| Fixed counter | A rough, inexpensive cap is enough | Boundary bursts can exceed the intended rolling rate | Discrete windows misrepresent rolling pressure |
| Sliding window | A rolling rate must be enforced accurately | Usually rejects excess work | Does not smooth work into a steady output rate |
| Leaky bucket | The protected system needs a steady drain rate | Buffers bursts up to a bounded queue | Fixed drain rate may lag changing capacity |
| Token bucket | Controlled bursts are acceptable | Saved tokens permit a bounded burst | Capacity and refill rate must both be tuned |

### Select excess-traffic behavior

- **Reject** early when waiting would miss the deadline or increase waste.
- **Degrade** when a safe reduced service exists.
- **Queue** only with a finite capacity and wait time; define overflow behavior.

For distributed enforcement, include coordination latency, consistency, availability, and the cost of collecting global state. A limiter must not consume more capacity than the work it protects. Approximation may be safer than precise global coordination when the cost of exactness is too high.
