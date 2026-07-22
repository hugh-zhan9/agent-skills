# Transactions

Start from business invariants and concrete interleavings, not isolation-level labels.

## Transaction Worksheet

For every command or transaction record:

| Field | Capture |
| --- | --- |
| Trigger | API, job, retry, webhook, manual operation |
| Reads | Rows, objects, predicates, aggregates, existence checks |
| Writes | Inserts, updates, deletes, state transitions |
| Constraints | Unique, foreign key, check, exclusion, app-only |
| Isolation | Actual product, version, configuration, and default |
| Retry | Automatic/manual retry, stable idempotency key, abort handling |
| External effects | Payments, email, queues, caches, APIs |

State the invariant in one sentence. Model at least one concurrent interleaving or prove that an atomic constraint rejects it.

## Anomaly Prompts

- **Dirty write:** can an uncommitted write be overwritten?
- **Dirty read:** can a decision observe data that later aborts?
- **Non-repeatable read:** can the same item change between reads within one logical decision?
- **Read skew:** can related reads observe mutually inconsistent points in time?
- **Lost update:** can two writers read one value and overwrite each other's derived update?
- **Write skew:** can writers update different items after both observe a predicate that stops being true?
- **Phantom:** can a concurrent insert/delete change a predicate, count, or absence check?
- **Duplicate execution:** can retry repeat a charge, allocation, insert, publish, or transition?
- **Serialization abort:** can the database reject a valid attempt, and is the whole transaction safely retried?

A snapshot that excludes a later concurrent commit is not automatically anomalous. Ask whether the snapshot is internally consistent and whether the business decision requires a fresher or serializable view.

## Mitigations

Match the mechanism to the invariant:

- Database constraints for expressible invariants.
- Atomic conditional updates for counters and state transitions.
- Compare-and-set or version columns for optimistic concurrency.
- Product-specific row or predicate locks when their coverage is proven.
- Serializable execution for predicate-based invariants, with complete-transaction retry.
- Unique/exclusion constraints for allocation and deduplication.
- Stable idempotency keys guarded atomically.
- Outbox/inbox or equivalent coordination for transactional state plus messages.

Do not perform non-idempotent external effects inside a transaction that may abort or retry. Defer them, use provider-supported idempotency, or establish an explicit recovery protocol.

## Required Evidence

- Named invariant and exact read/write/predicate set.
- Minimal two-or-more-transaction interleaving.
- Exact database semantics from current official documentation.
- Constraint or concurrency tests that reject bad states.
- Serialization-abort and full-transaction-retry tests.
- Duplicate-request and external-side-effect tests.
- Recovery behavior for uncertain outcomes and partial failures.
