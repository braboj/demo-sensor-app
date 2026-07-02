# 9. Architecture Decisions

The significant architectural decisions are recorded as individual Architecture
Decision Records (ADRs) under [`docs/decisions/`](../decisions/). This chapter is
the index: each row links to the full record. The decisions are consistent with
the constraints in [Chapter 2](02-architecture-constraints.md) and the strategy
in [Chapter 4](04-solution-strategy.md).

Each new ADR is added as a row here and to the
[decisions README](../decisions/README.md), which records the ADR format
(Status / Context / Decision / Consequences).

| ID | Decision | Category | Status |
| --- | --- | --- | --- |
| ADR-0001 | [Data generator runs as a dedicated worker process](../decisions/0001-data-generator-as-worker-process.md) | architecture | Accepted |
| ADR-0002 | [CI gates only currently-green checks; strict gates phase in](../decisions/0002-ci-gates-green-subset.md) | process | Accepted |
| ADR-0003 | [Production frontend served by nginx with a same-origin `/api` proxy](../decisions/0003-frontend-nginx-same-origin-proxy.md) | architecture | Accepted |
| ADR-0004 | [In-process data generator on the free hosting tier](../decisions/0004-inprocess-generator-free-tier.md) | deployment | Accepted |
| ADR-0005 | [Real-time delivery via Server-Sent Events](../decisions/0005-realtime-delivery-sse.md) | architecture | Accepted |
| ADR-0006 | [Gate CI on `mypy --strict`](../decisions/0006-gate-mypy-strict.md) | process | Accepted |
| ADR-0007 | [Deploy Grafana to the live Render stack](../decisions/0007-deploy-grafana-on-render.md) | deployment | Accepted |
| ADR-0008 | [Embed the Grafana dashboard in the SPA](../decisions/0008-embed-grafana-in-spa.md) | architecture | Accepted |
| ADR-0009 | [Trigger Render deploys with a CI deploy hook, not push-based autoDeploy](../decisions/0009-render-deploy-hook-trigger.md) | deployment | Superseded by ADR-0010 |
| ADR-0010 | [Scale multi-service Render deploys with a manifest-driven CI matrix](../decisions/0010-scalable-render-deploy-manifest-matrix.md) | deployment | Accepted (target design) |
| ADR-0011 | [arc42 architecture documentation](../decisions/0011-arc42-documentation.md) | docs | Accepted |
