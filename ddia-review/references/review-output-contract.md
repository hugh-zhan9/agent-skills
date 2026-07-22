# Review Output Contract

Use this contract for focused and broad reviews. Prioritize decisions over checklist coverage. Scope every verdict to the reviewed question or artifact; use an overall launch verdict only for a launch-readiness or broad architecture request.

## Verdict

Choose one:

- `ready`: no known blocker remains within the reviewed scope and the evidence is sufficient.
- `conditionally ready`: no known P0/P1 blocker remains, but named nonblocking mitigations, measurements, or operational gates are still required.
- `not ready`: at least one known P0/P1 blocker remains within the reviewed scope.
- `insufficient evidence`: a missing product guarantee, workload fact, or design detail could reveal or remove a P0/P1 blocker.

State the scope and the modules reviewed. Do not imply that unreviewed security, privacy, regulatory, or business concerns passed.

## Findings

Order findings by severity:

- `P0`: credible risk of irreversible corruption, materially unsafe external side effects, or catastrophic loss requiring immediate redesign.
- `P1`: launch blocker for a required correctness, durability, availability, or compatibility promise.
- `P2`: material risk that needs mitigation, measurement, or an explicit product decision.
- `P3`: improvement, maintainability concern, or low-impact uncertainty.

For every P0/P1 finding provide all fields below. For P2/P3 findings, combine fields when clarity is preserved, especially when the user asks for a concise review.

1. **Claim**: one precise sentence describing the defect or unproven assumption.
2. **Evidence**: the relevant path, configuration, sequence, measurement, or missing proof.
3. **Promise or invariant**: what can be violated.
4. **Failure scenario**: the shortest concrete interleaving or event sequence that exposes the problem.
5. **Impact**: user-visible and operational consequences.
6. **Recommendation**: the smallest sufficient mitigation or safer alternative.
7. **Verification**: test, metric, drill, constraint, or official product guarantee needed.
8. **Launch blocker**: `yes`, `no`, or `unknown`.

Distinguish observed facts, user-provided claims, inferences, and assumptions. Do not assign high severity merely because a design is unconventional.

## Decision Summary

End with:

- Required changes before launch.
- Important follow-up evidence.
- Accepted tradeoffs and their owners, when known.
- Residual risks after the recommendations.

If no material finding exists, say so and list the evidence reviewed and remaining uncertainty. Never manufacture findings to fill the format.
