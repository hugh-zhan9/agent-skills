# Source and Scope

## Conceptual Basis

This skill operationalizes concepts from Martin Kleppmann's *Designing Data-Intensive Applications*, first edition (2017):

| Modules | First-edition conceptual map |
| --- | --- |
| Quality Baseline | Chapter 1: reliability, scalability, maintainability |
| Data Design | Chapters 2–3: data models, query languages, storage, indexes, analytics |
| Schema Evolution | Chapter 4: encoding, compatibility, dataflow across boundaries |
| Distribution | Chapters 5–6: replication and partitioning |
| Transactions | Chapter 7: isolation, anomalies, serializability |
| Distributed Failures | Chapters 8–9: partial failure, clocks, consistency, ordering, consensus |
| Pipelines | Chapters 10–12: batch, streams, derived data, integration, correctness |

The checklists and workflow are original review material, not excerpts or a book summary.

## Edition Boundary

The module map follows the first edition. It does not claim complete coverage of the second edition or every modern product and research development. Keep terminology edition-neutral where possible and update this file when deliberately incorporating later-edition material.

## Review Boundary

DDIA reasoning is strong for data correctness, distribution, evolution, and operational tradeoffs. It is not by itself a complete review of:

- Security and abuse resistance.
- Privacy, retention law, and regulatory compliance.
- Financial, medical, or other domain-specific controls.
- User experience, product value, cost, or organizational feasibility.
- Product-specific implementation guarantees.

State these limits in broad architecture reviews and add the appropriate specialist review when the decision depends on them.
