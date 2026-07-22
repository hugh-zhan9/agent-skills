# Pipelines

Review batch, stream, CDC, event-sourced, materialized-view, cache, search, warehouse, and other derived-data flows end to end.

## Map the Flow

Record:

- Authoritative input or source of truth and its durable commit point.
- Extraction: query, log tailing, CDC, outbox, event publish, or batch export.
- Transport, partitioning, retention, and delivery semantics.
- Processor state: offsets, checkpoints, windows, aggregates, caches, and versions.
- Sink or derived store commit point.
- Acknowledgement/checkpoint point and retry behavior.
- Rebuild, reconciliation, repair, and backfill paths.

Trace one record from source commit through publication, delivery, processing, sink commit, acknowledgement, replay, and recovery.

## Atomicity Proof Obligations

Require explicit evidence for both boundaries:

1. **Source mutation plus publication:** use transaction-log CDC, a transactional outbox, a proven atomic protocol, or a reconciliation process that can detect and recover a committed mutation whose event was never published.
2. **Sink mutation plus progress:** atomically commit sink state with its offset/checkpoint, or make processing durably idempotent and safely repeatable after any crash point.

Idempotency handles duplicates; it does not recover an event that was never durably captured. Broker transactions do not automatically cover databases, search indexes, payments, email, or other external effects.

## Correctness Checks

- **Duplicates:** stable identity, durable deduplication, idempotent state transitions and side effects.
- **Missing data:** detectable gaps across deploy, rebalance, retention, offset reset, and partial publication.
- **Ordering:** required scope—per entity, key, partition, causal relation, or global—and stale-update rejection.
- **Replay/backfill:** historical schemas, deterministic logic, side-effect suppression, and interaction with live writes.
- **Time:** event versus processing time, watermarks, lateness, corrections, clock skew, and time zones.
- **Divergence:** source/derived comparison, staleness visibility, repair, and rebuild time.

Treat `exactly once` as a scoped product claim. Verify the full chain of side effects and retries before using it as an application guarantee.

## External Side Effects

For payments, email, webhooks, or third-party APIs require stable idempotency keys, durable intent/state, uncertain-outcome recovery, and replay protection. An inbox transaction cannot make an external provider atomic; use provider-supported idempotency or reconciliation.

## Required Evidence

- Proof or recovery mechanism for source-publication atomicity.
- Proof or repeatability mechanism for sink-checkpoint atomicity.
- Kill-point tests before and after every commit and acknowledgement boundary.
- Duplicate, missing, out-of-order, replay, and concurrent-backfill tests.
- Historical schema compatibility plan.
- Divergence metric, reconciliation process, and measured rebuild procedure.
- Lag, backlog, retry, dead-letter, deduplication, and repair observability.
