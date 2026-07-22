# Quality Baseline

Apply this baseline to broad architecture, launch-readiness, reliability, scalability, capacity, performance, durability, or recovery reviews before loading specialized modules.

## Boundary and Promises

Record:

- Users, upstream producers, downstream consumers, operators, and external systems inside the review boundary.
- User-visible success semantics: what an acknowledgement, confirmation, or completed state promises.
- Business invariants and unacceptable outcomes.
- Authoritative inputs, systems of record, derived data, and recovery sources.
- Assumptions that remain outside the boundary.

## Workload

Replace vague scale language with:

- Request or event rate by operation, including bursts and seasonality.
- Read/write ratio, fanout, hot keys, skew, and largest tenant/entity.
- Data volume, retention, growth, backfill, and replay load.
- Expensive query shapes, joins, scans, aggregates, and side effects.
- Current measurements, target horizon, and expected headroom.

## Measurable Promises

Require the applicable targets:

| Attribute | Evidence to request |
| --- | --- |
| Availability | SLO, measurement window, excluded failure classes, degradation behavior |
| Latency | Percentiles by operation, concurrency, payload and data-set assumptions |
| Throughput | Sustained and burst targets, saturation point, queueing behavior |
| Durability | Which acknowledged writes must survive which failures |
| RPO | Maximum acceptable loss of acknowledged or source data |
| RTO | Maximum time to restore the promised service and correctness |
| Freshness | Maximum tolerated replication, index, cache, or analytical lag |
| Correctness | Invariants, consistency guarantees, deduplication and reconciliation expectations |
| Capacity | Growth horizon, resource limit, rebalance or expansion plan |

Do not substitute average latency for tail latency or restore time for data-loss tolerance.

## Reliability and Operations

Check hardware, software, overload, dependency, data-corruption, human, deployment, migration, and regional failures. Require:

- Backups plus tested restore procedures.
- Dashboards for health, saturation, lag, backlog, correctness, and divergence.
- Alerts tied to user promises rather than host health alone.
- Safe runbooks for common incidents and rollback.
- Failure drills that cover the stated RPO and RTO.

## Maintainability

Review:

- Operability: can operators detect, diagnose, contain, and repair failures?
- Simplicity: are ownership and failure paths understandable without hidden coupling?
- Evolvability: can schemas, capacity, dataflows, and implementations change incrementally?

## Required Evidence

- Named invariants and success semantics.
- Load model and performance test plan.
- SLO, RPO, RTO, freshness, and durability targets where applicable.
- Failure-mode table and recovery evidence.
- Metrics, alerts, runbooks, migration, and rollback plans.
