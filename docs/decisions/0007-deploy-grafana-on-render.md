# ADR-0007 — Deploy Grafana to the live Render stack

**Status:** Accepted (2026-06-30, issue #72)

## Context
#7 provisioned Grafana as code (datasource + "Sensor Readings" dashboard) for
the local docker-compose stack, and #67 added an in-app "View charts in Grafana"
link gated on `environment.grafanaUrl`. The free-tier Render Blueprint (#55,
ADR-0004) deployed only `db` + `backend` + `frontend`, so `environment.prod.ts`
shipped `grafanaUrl: ''` and the link stayed hidden in production — the live
site showed the table + SSE stream but no charts. The owner asked for Grafana on
the live deploy.

Two constraints shape the design:

- Render's free tier has **no persistent disk**, so a stock Grafana image would
  lose its datasource/dashboards on every restart.
- Render's `fromDatabase` Blueprint reference exposes the managed Postgres as a
  **connection string** (and `user`/`password`/`database`), but **not** the
  `host`/`port` individually — yet Grafana's Postgres datasource needs
  `host:port`.

## Decision
Add a fourth Render service, `sensor-app-grafana`, built from a thin
`deploy/grafana/Dockerfile`:

- **Bake the provisioning into the image** (`COPY provisioning
  /etc/grafana/provisioning`) instead of mounting a volume, so the datasource
  and dashboard reload on every boot regardless of the missing disk. The image
  is pinned to `grafana/grafana:11.4.0`, matching the compose stack.
- A small **entrypoint** (`render-entrypoint.sh`) binds Render's injected
  `$PORT` (Grafana reads `GF_SERVER_HTTP_PORT`) and parses the managed DB's
  `DATABASE_URL` into the `POSTGRES_HOST/PORT/USER/PASSWORD/DB` variables the
  datasource YAML interpolates. When `DATABASE_URL` is unset (docker-compose),
  the `POSTGRES_*` vars are passed directly and parsing is skipped.
- The datasource YAML is **parameterized** (`url: ${POSTGRES_HOST}:${POSTGRES_PORT}`,
  `sslmode: ${POSTGRES_SSLMODE}`) so one file serves both contexts: compose
  passes `disable`, Render passes `require` (managed PG mandates SSL).
- **Anonymous Viewer access** (`GF_AUTH_ANONYMOUS_ENABLED=true`,
  `GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer`) so the public link works without a login;
  sign-up is disabled and the admin password is generated, never committed.
- The frontend service sets `GRAFANA_URL` so `set-api-url.mjs` bakes the
  dashboard link into the production bundle; the link surfaces in the SPA.

## Consequences
- The live demo now reaches the charts; the compose path is unchanged (same
  provisioning files, same pinned image).
- **Free-tier caveats:** the Grafana web service spins down when idle, so the
  first hit after idle cold-starts (~30–60 s); there is no persistent disk, so
  any manual changes and the admin password reset on restart — acceptable
  because the datasource and dashboards are provisioned as code and viewing is
  anonymous. A second free web service also draws on the account's shared free
  instance hours.
- **Three service hostnames** are now derived from service names in
  `render.yaml` (`CORS_ORIGINS`, `API_URL`, `GRAFANA_URL` + `GF_SERVER_ROOT_URL`).
  If Render suffixes a taken name, all of these must be reconciled and redeployed
  (see `docs/DEPLOY.md`).
- Validated locally end-to-end before shipping: the image builds with
  provisioning baked, the entrypoint parses Render-style connection strings
  (with/without an explicit port, with a `+driver` scheme and query), Grafana
  connects to Postgres ("Database Connection OK"), the dashboard panel SQL
  returns worker rows, and an anonymous visitor can query and view the
  dashboard. The actual TLS handshake against Render's managed PG is the only
  step not exercisable locally.
- This extends ADR-0004 (which deliberately kept Grafana out of the free-tier
  deploy); that constraint is now lifted for `sensor-app-grafana`.
