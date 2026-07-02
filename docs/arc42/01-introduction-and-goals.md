# 1. Introduction and Goals

Sensor Dashboard is a small multi-service demo that simulates the sensor
readings of an industrial plant. A background simulator produces readings —
temperature, humidity, and a vibration flag — at a fixed interval; the readings
are stored, served over a REST API, streamed to a web page as they arrive, and
charted. The result is a compact but complete slice of a monitoring system: data
generation, storage, an API, a live web view, and a dashboard.

## 1.1 Requirements overview

A functional requirement states what the system does. Qualities such as
reliability and usability — sometimes called non-functional requirements — are
covered separately by the quality goals.

| ID | Requirement |
|------|-------------|
| FR01 | The system shall generate simulated sensor readings — temperature, humidity, and a vibration flag — at a fixed interval. |
| FR02 | The system shall store every reading durably, with the time it was recorded. |
| FR03 | The system shall serve the stored readings over an HTTP REST API. |
| FR04 | The system shall let a caller bound how many readings are returned, and reject an invalid bound with a clear error. |
| FR05 | The system shall stream newly recorded readings to connected clients in real time. |
| FR06 | The system shall present the readings on a web page, with explicit loading, empty, and error states. |
| FR07 | The system shall visualize the readings as time-series charts. |
| FR08 | The system shall expose health and readiness checks for its operators. |

## 1.2 Quality goals

Quality goals describe how well the system works, rather than what it does. They
are also known as quality attributes or non-functional requirements.

| ID | Quality goal | Motivation |
|------|--------------|------------|
| QG01 | Correctness | Readings are stored and returned faithfully: newest first, bounded on request, with timestamps in a single unambiguous format. |
| QG02 | Reliability | Bad input fails predictably with an HTTP 400 and a JSON error; a failed write never poisons the next one; the web page never shows a silent blank screen. |
| QG03 | Maintainability | Clean, readable, well-tested code across both stacks: a clear layout, type checks, linting, and coverage gates. |
| QG04 | Portability | Each service is a pinned container; the same images run under local Docker Compose and on a hosted platform. |
| QG05 | Observability | The running system is legible: structured logs, a shallow liveness check, and a deep readiness check that reports whether the database is reachable. |
| QG06 | Usability | An evaluator can run and explore the whole stack quickly: a one-command local stack, a live table, an embedded dashboard, and a hosted demo. The web page is accessible. |
| QG07 | Security | No secrets in the repository, a scoped cross-origin policy, no debug server in any shipped image, and validated input at every boundary. |

## 1.3 Stakeholders

Stakeholders are the people with an interest in the system, and this section
lists their expectations from it.

| Role | Concern |
|------|---------|
| Interviewer / prospective client | Quickly assess engineering quality: clean multi-service code, sound decisions, and a running demo. |
| Maintainer | Exemplary, testable, low-maintenance code that passes its quality gates and deploys cleanly as the demo. |
| Operator | Run the stack and tell at a glance whether it is alive and whether it is ready to serve — and diagnose it from its logs. |
