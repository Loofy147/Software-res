# Architecture

```text
Developer / AI Agent
        |
        v
AI Code Reliability
        |
        v
Verification
        |
        v
Runtime & Concurrency Compatibility
        |
        v
Ecosystem Migration Stability
        |
        v
Semantic Observability / Corruption Detection
        |
        v
Human Governance
        |
        +-----------------------------+
                                      |
Cross-cutting: Reproducibility & Dependency Integrity
                                      |
                                      v
                              Evidence / Provenance
                                      |
                                      v
                              Reliability Vector
                                      |
                          +-----------+-----------+
                          |           |           |
                        MERGE       REVIEW      REJECT
```

The implementation uses SLSA/in-toto as the provenance substrate and adds AI-specific evidence and project-specific Reliability Vector references instead of inventing a closed provenance protocol.
