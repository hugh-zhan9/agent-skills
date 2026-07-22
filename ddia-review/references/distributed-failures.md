# Distributed Failures

Expose assumptions about time, leadership, ownership, ordering, communication, and failure.

## Model the Assumptions

Classify two independent dimensions:

1. **Timing model:** synchronous, partially synchronous, or asynchronous assumptions about processing and network delay.
2. **Failure model:** crash-stop, crash-recovery, omission, arbitrary/Byzantine, or a product-specific model.

Then state which claims are about safety (nothing incorrect happens) and which are about liveness or availability (progress eventually occurs). A timeout can support liveness decisions; it does not prove another process is dead.

## Assumption Inventory

Record every place the design assumes:

- A node is alive because it responded recently, or dead because it timed out.
- A clock is accurate enough for order, expiry, TTL, or conflict resolution.
- A lease holder, leader, coordinator, or lock owner is still exclusive.
- Messages arrive once, in order, or before a deadline.
- Quorums overlap in the way application correctness requires.
- A retry is harmless.
- A coordinator or distributed transaction can block without unacceptable impact.

## Failure Scenarios

Apply network partitions, long delay, process pause, clock jump, retry, duplicate, reordering, stale leader, membership change, and coordinator failure. Include:

- A delayed request arriving after ownership changed.
- An old process resuming after its lease expired.
- A coordinator failing after only some participants prepared or committed.
- A promoted leader and old leader both continuing to act.
- A timeout firing while the original operation later succeeds.

## Mechanisms

Require only the mechanism the invariant needs:

- Fencing tokens or monotonically increasing epochs enforced by the protected resource.
- Compare-and-set or version checks for stale writers.
- Idempotency and durable deduplication for uncertain retries.
- Per-key, causal, partition, or total order at the narrowest sufficient scope.
- Consensus when nodes must agree despite the declared timing/failure model.
- Explicit partition behavior choosing correctness and availability promises.

Do not treat leases, locks, quorum counts, or leader election as self-proving. Verify the protected resource rejects stale actors.

## Required Evidence

- Timing/failure model and safety/liveness claims.
- Failure-mode table with expected behavior.
- Product documentation for locks, leases, quorum, consensus, membership, and transactions.
- Tests or drills for pause, timeout, retry, stale actor, partition, and recovery.
- Metrics for leadership/epoch changes, fencing rejects, retries, duplicates, and coordinator recovery.
