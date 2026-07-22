# Distribution

Review replication and partitioning against required consistency, locality, scale, durability, and recovery behavior.

## Topology

Record:

- Write acceptance, read serving, routing, and regional placement.
- Leader/follower, multi-leader, leaderless/quorum, sharded, or mixed topology.
- Synchronous, asynchronous, semi-synchronous, quorum, or product-defined replication.
- Replica rebuild, catch-up, failover, rebalance, and client metadata behavior.
- Which acknowledgement point defines success and its durability/RPO consequence.

## Required Guarantees

Ask which guarantees are user or application requirements:

- Read-your-writes: a client sees its successful write.
- Monotonic reads: a client does not move backward in observed state.
- Consistent prefix: if write B follows A in the relevant order, a reader must not observe B without first or simultaneously observing A.
- Conflict preservation: concurrent writes are detected, retained, rejected, or merged instead of silently overwritten.
- Bounded staleness: stale reads stay within a measured time or version bound.
- Regional continuity: isolation behavior matches an explicit correctness/availability choice.

Do not infer these guarantees from replication or quorum settings alone.

## Replication Risks

- Post-write reads routed to a lagging replica.
- Routing changes that violate session guarantees.
- Acknowledged writes lost during async failover.
- Concurrent writes resolved by unsafe timestamps or silent last-write-wins.
- Old values resurfacing through repair, hinted handoff, or divergent replicas.
- A stale leader, relay, or replica continuing to serve after promotion.

Require product-specific evidence for lag, acknowledgement, conflict, quorum, failover, fencing, and rebuild semantics.

## Partitioning

For each candidate key evaluate distribution, locality, hot-key risk, secondary indexes, global constraints, routing, rebalance, and future repartitioning.

- Hash partitioning usually disrupts ordered range access and locality on the hashed dimension; compound, bucketed, or local index designs may preserve other locality.
- Range partitioning can support ordered scans but may skew under uneven distributions or monotonic writes; it does not inherently skew.
- Tenant keys can fail when tenant sizes are highly unequal.
- Time keys can create a hot current range.
- Global indexes, scatter/gather, cross-partition joins, and transactions can become the true bottleneck.

## Required Evidence

- Required consistency and durability guarantees.
- Realistic key-distribution sample, top-N hot keys, and growth horizon.
- Local/global query and index plans.
- Replication lag, replay position, routing, conflict, skew, and failover metrics.
- Failover and rebalance drills with lagging nodes and in-flight writes.
- Repartition, backfill, rollback, divergence, and repair procedures.
