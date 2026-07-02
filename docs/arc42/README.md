# Architecture (arc42)

The architecture of Sensor Dashboard, documented with the
[arc42](https://arc42.org) template. Each chapter builds on the ones before it
and avoids assuming detail introduced later, so the set reads top-to-bottom as a
guided tour of the system as well as a reference.

| # | Chapter | What it covers |
|---|---------|----------------|
| 1 | [Introduction and Goals](01-introduction-and-goals.md) | What the system does, its quality goals, and its stakeholders. |
| 2 | [Architecture Constraints](02-architecture-constraints.md) | The fixed technical, organizational, and security constraints. |
| 3 | [Context and Scope](03-context-and-scope.md) | The system boundary: who and what it talks to, and what is in/out of scope. |
| 4 | [Solution Strategy](04-solution-strategy.md) | The fundamental decisions, mapped to requirements and quality goals. |
| 5 | [Building Block View](05-building-block-view.md) | The static decomposition into services and, within them, code. |
| 6 | [Runtime View](06-runtime-view.md) | How the blocks collaborate: generating, reading, streaming, failing. |
| 7 | [Deployment View](07-deployment-view.md) | Local Compose and hosted topologies, and the CI/CD pipeline. |
| 8 | [Crosscutting Concepts](08-crosscutting-concepts.md) | Concepts spanning blocks: config, persistence, errors, SSE, security. |
| 9 | [Architecture Decisions](09-architecture-decisions.md) | The index of ADRs. |
| 10 | [Quality Requirements](10-quality-requirements.md) | The quality tree and concrete, testable scenarios. |
| 11 | [Risks and Technical Debt](11-risks-and-technical-debt.md) | Known risks and the gaps against the target conventions. |
| 12 | [Glossary](12-glossary.md) | Domain and technical terms. |

The decision to adopt arc42 (and to drop the static-site/Pages scope) is recorded
in [ADR-0011](../decisions/0011-arc42-documentation.md).
