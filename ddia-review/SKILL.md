---
name: ddia-review
description: Review data-intensive systems and changes using DDIA-derived reasoning. Use for broad architecture reviews or focused questions about reliability, scalability, maintainability, data models, storage, indexes, schema compatibility, replication, sharding, multi-region consistency, transaction isolation, concurrency, clocks, leases, failover, consensus, batch, stream, CDC, event-driven systems, caches, search indexes, or other derived-data pipelines.
---

# DDIA Review

Turn architecture claims into explicit promises, invariants, failure scenarios, evidence, and prioritized decisions. Review the user's actual design; do not produce a generic DDIA summary.

## Process

1. Define the scope, user-visible promises, business invariants, authoritative data, and important unknowns.
2. Read [Quality Baseline](references/quality-baseline.md) for broad architecture, launch-readiness, reliability, scalability, capacity, performance, durability, or recovery reviews. For a focused question, apply only the relevant promise and invariant from step 1.
3. Select the applicable modules from the routing table. Read each selected reference completely.
4. Trace concrete read, write, commit, replication, delivery, retry, failover, migration, and recovery paths before judging the design.
5. Separate correctness, durability, availability, performance, operability, and evolvability claims.
6. Verify correctness-critical product behavior against current official product documentation when the user has not supplied authoritative evidence.
7. Return findings using [Review Output Contract](references/review-output-contract.md). Scope the verdict to the question; do not imply an overall launch verdict for a focused review.

Proceed with explicit assumptions when non-critical context is missing. Mark a conclusion as `insufficient evidence` when the missing fact could reverse it.

## Module Routing

| Signals in the request | Read |
| --- | --- |
| Broad architecture, launch readiness, reliability, scale, capacity, performance, durability, SLO, RPO, RTO, recovery | [Quality Baseline](references/quality-baseline.md) |
| Relationships, SQL/document/graph, normalization, storage engines, indexes, materialized views, OLTP/OLAP | [Data Design](references/data-design.md) |
| Schema, serialized records, events, RPC contracts, rolling deploys, replay, backfill | [Schema Evolution](references/schema-evolution.md) |
| Replicas, lag, consistency, shards, partition keys, regions, routing, rebalance, failover | [Distribution](references/distribution.md) |
| Isolation levels, concurrent writes, constraints, allocation, balance, oversell, retries, idempotent commands, uncertain outcomes | [Transactions](references/transactions.md) |
| Timeouts, clocks, leases, locks, fencing, leaders, quorum, ordering, consensus, coordinators, distributed transactions, 2PC, partitions | [Distributed Failures](references/distributed-failures.md) |
| Batch, stream, Kafka, CDC, outbox, event sourcing, replay, cache, search, warehouse, derived state, payments, email, webhooks, external side effects | [Pipelines](references/pipelines.md) |

For a broad architecture request, scan every routing row, select every module evidenced by the design, and deepen only the material risks. State which modules were and were not reviewed.

## Common Combinations

- Database mutation plus event publication: Transactions + Pipelines.
- Async replication plus automatic failover: Distribution + Distributed Failures.
- Event or RPC format rollout: Schema Evolution; add Pipelines for retained messages, replay, or CDC.
- Sharding plus global indexes or constraints: Data Design + Distribution; add Transactions for cross-shard invariants.
- Event-sourced projections: Schema Evolution + Transactions + Pipelines.
- Retry or replay around a payment, webhook, or other external effect: Transactions + Pipelines.
- Distributed transaction, coordinator recovery, or 2PC: Transactions + Distributed Failures.

## Guardrails

- Do not infer correctness from names such as `serializable`, `snapshot`, `quorum`, `exactly once`, `distributed lock`, or `schema registry`.
- Do not recommend a technology, index, partition key, consistency level, or isolation level without tying it to a workload, invariant, or user-visible promise.
- Do not confuse detection with mitigation: require a mechanism and evidence for every launch-blocking failure mode.
- Do not treat a transport guarantee as an end-to-end application guarantee.
- Do not invent product semantics. Label them for verification and prefer official documentation.
- Keep security, privacy, regulatory, financial-domain, and organizational risks explicitly out of scope unless the review includes evidence for them.

Read [Source and Scope](references/source-and-scope.md) only when provenance, edition coverage, or the limits of the DDIA lens matter.
