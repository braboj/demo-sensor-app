# Architecture Decision Records

Short records of significant, non-obvious decisions. One file per decision,
numbered. Format: Status / Context / Decision / Consequences.

- [ADR-0001](0001-data-generator-as-worker-process.md) — Data generator runs as a dedicated worker process
- [ADR-0002](0002-ci-gates-green-subset.md) — CI gates only currently-green checks; strict gates phase in
- [ADR-0003](0003-frontend-nginx-same-origin-proxy.md) — Production frontend served by nginx with a same-origin /api proxy
- [ADR-0004](0004-inprocess-generator-free-tier.md) — In-process data generator on the free hosting tier (Render)
- [ADR-0005](0005-realtime-delivery-sse.md) — Real-time delivery via Server-Sent Events
- [ADR-0006](0006-gate-mypy-strict.md) — Gate CI on mypy --strict
- [ADR-0007](0007-deploy-grafana-on-render.md) — Deploy Grafana to the live Render stack
- [ADR-0008](0008-embed-grafana-in-spa.md) — Embed the Grafana dashboard in the SPA
- [ADR-0009](0009-render-deploy-hook-trigger.md) — Trigger Render deploys with a CI deploy hook, not push-based autoDeploy
