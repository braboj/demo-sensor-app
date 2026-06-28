# Architecture Decision Records

Short records of significant, non-obvious decisions. One file per decision,
numbered. Format: Status / Context / Decision / Consequences.

- [ADR-0001](0001-data-generator-as-worker-process.md) — Data generator runs as a dedicated worker process
- [ADR-0002](0002-ci-gates-green-subset.md) — CI gates only currently-green checks; strict gates phase in
- [ADR-0003](0003-frontend-nginx-same-origin-proxy.md) — Production frontend served by nginx with a same-origin /api proxy
- [ADR-0004](0004-inprocess-generator-free-tier.md) — In-process data generator on the free hosting tier (Render)
