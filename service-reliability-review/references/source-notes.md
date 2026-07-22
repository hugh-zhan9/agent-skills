# Source Notes

This skill combines selected sections of Zhou Zhiming's *The Fenix Project* (`the-fenix-project.pdf`, release 2021-12-26). Page numbers refer to the supplied 658-page PDF.

| Skill content | Source location | Operational transformation |
| --- | --- | --- |
| Failure policies, circuit breaking, isolation, retries, degradation, and bounded attempts | Pages 323–336, “Service Fault Tolerance” | Explanatory patterns were reorganized into a dependency-level selection and review workflow |
| Pressure measurements, admission behavior, sliding windows, leaky/token buckets, and distributed limiting tradeoffs | Pages 337–345, “Traffic Control” | Algorithm descriptions were converted into overload decision criteria and failure checks |
| Event logging, correlation identifiers, sensitive-data and diagnostic-log guardrails, collection and buffering | Pages 368–374, “Event Logs” | Logging guidance was converted into a control-transition evidence contract |
| Trace/span relationships, performance overhead, collection approaches, and standardization | Pages 375–382, “Distributed Tracing” | Concepts were converted into critical-path, retry-attempt, and control-decision trace requirements |
| Metric types, collection, storage, visualization, and alerting | Pages 383–391, “Aggregated Metrics” | Concepts were converted into baseline and control-specific signals with operator actions |

## Interpretation Limits

- Specific product examples and defaults in the source reflect its 2021 publication date. This skill deliberately avoids prescribing Hystrix, OpenTracing, Elastic Stack, Prometheus, or any other product.
- Current product behavior, default thresholds, protocols, and instrumentation semantics must be verified against the project's pinned version and current official documentation.
- The combined control-to-observability matrix, verdicts, report contract, test scenarios, and evidence rules are an original operational synthesis rather than copied source passages.
