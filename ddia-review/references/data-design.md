# Data Design

Design logical models, physical storage, and access paths together.

## Domain and Access Paths

Classify relationships as one-to-one, one-to-many, many-to-many, hierarchical, graph-like, temporal, aggregate-oriented, or append-only. Record the important:

- Point lookups, range scans, joins, traversals, sorts, and pagination.
- Inserts, updates, deletes, update fanout, and contention.
- Atomicity and integrity requirements.
- Ad hoc queries, reports, analytical scans, and freshness needs.
- Schema evolution, migration, backfill, retention, and ownership.

## Logical Model

| Option | Useful when | Watch for |
| --- | --- | --- |
| Relational | Joins, constraints, flexible queries, many-to-many relationships | Migration cost, mapping friction, distributed joins |
| Document | Aggregate locality, hierarchical reads, heterogeneous records | Duplication, cross-document invariants, partial updates, query limits |
| Graph | Relationship traversal is the central workload | Query cost, operational maturity, team familiarity |
| Denormalized | Known reads dominate and update propagation is controlled | Write fanout, stale copies, repair and rebuild logic |
| Append-only/event-shaped | History, audit, replay, or temporal reasoning is central | Projection correctness, semantic evolution, storage growth |
| Hybrid | Different workloads require different representations | Authority, synchronization, rebuildability, operational ownership |

Do not equate a flexible physical format with the absence of a schema. Name the semantic schema and its enforcement point.

## Storage and Indexes

Collect point/range mix, write rate, burstiness, churn, cardinality, selectivity, retention, compaction pressure, analytical scan volume, and freshness targets.

| Option | Useful when | Watch for |
| --- | --- | --- |
| Hash-style access | Exact-key lookup dominates | No ordered access on the hashed dimension, rebuild cost |
| B-tree-like index | Ordered traversal and range scans matter | Page churn, random writes, cache behavior |
| LSM-like storage | Write throughput and sequential flushing matter | Compaction, read/write amplification, tombstones |
| Secondary index | A named non-primary query path matters | Write cost, consistency, local versus global behavior |
| Column-oriented store | Analytics scans a subset of columns | Point updates, row reconstruction, serving freshness |
| Materialized view | A repeated derived query is expensive | Update coupling, staleness, rebuild, reconciliation |
| Separate analytical store | Analytics interferes with serving work | Pipeline correctness, freshness, duplicate ownership |

Do not recommend an index without naming the query, expected selectivity, write/storage cost, and online backfill behavior it serves.

## Review Questions

- Which integrity rules are enforced atomically, and which are only conventions?
- Which data should not be embedded, duplicated, or independently owned?
- Which queries become harder under the chosen model?
- Can indexes and views be built, rolled back, and repaired online?
- Will analytical work harm serving latency or recovery?
- What product behavior must be verified for planners, compaction, indexes, and constraints?

## Required Evidence

- Representative reads and writes with frequency and latency targets.
- Relationship and access-path map.
- Cardinality, selectivity, skew, and growth estimates.
- Integrity and ownership decisions.
- Query plans or product-specific evidence for critical access paths.
- Migration, backfill, rollback, and repair plans.
