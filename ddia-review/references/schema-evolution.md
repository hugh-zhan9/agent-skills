# Schema Evolution

Review any format change that crosses time, process, service, storage, queue, replay, or recovery boundaries.

## Inventory

Record:

- Every writer: services, jobs, migrations, manual tools, SDKs, tests, and importers.
- Every reader: services, analytics, exports, indexers, caches, consumers, and replay jobs.
- Stored data: rows, documents, objects, logs, snapshots, backups, and retained events.
- Transport data: RPC requests/responses, queue messages, events, and CDC records.
- Old/new version overlap and rollback window.

## Compatibility Matrix

Fill each cell with `pass`, `fail`, `unknown`, or `not applicable`:

| Writer | Reader | Meaning | Required evidence |
| --- | --- | --- | --- |
| old | old | Baseline | Existing fixture/test |
| old | new | Backward compatibility | Old fixture read by new code |
| new | old | Forward compatibility | New fixture read by old code |
| new | new | Target behavior | New fixture/test |

Classify additive, removal, rename, type, unit, precision, cardinality, default, requiredness, enum, semantic, and routing changes separately.

## Risk Checks

- Distinguish absent, null, empty, zero, and default where semantics require it.
- Verify unknown-field and unknown-enum behavior for every relevant language and serializer.
- Include historical replay, offline consumers, CDC, backups, and manual tools.
- Check partition, routing, idempotency, deduplication, and aggregate-version fields.
- Treat meaning changes with the same shape as schema changes.
- Verify rollback after new data has already been persisted or published.

Do not treat a schema registry or serialization format as proof of semantic compatibility.

## Rollout

Prefer expand-and-contract:

1. Teach readers to accept old and new representations.
2. Deploy compatible readers.
3. Begin writing the new representation.
4. Backfill when necessary and safe.
5. Prove no incompatible reader remains, including offline and replay consumers.
6. Remove the old representation in a later release.

Use shadow fields or dual writes only when both representations are updated atomically in the same authoritative record, or when a cross-system design has explicit reconciliation and repair. Never imply that two independent writes are atomic.

## Required Evidence

- Completed compatibility matrix.
- Old/new fixtures and semantic assertions.
- Serializer and product documentation for defaults, unknown values, and coercion.
- Migration/backfill dry-run and rollback test.
- Decode-failure, poison-message, and unexpected-value monitoring.
- Historical replay test when old data can re-enter the system.
