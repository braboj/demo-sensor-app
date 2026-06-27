# ADR-0003 — Production frontend served by nginx with a same-origin /api proxy

**Status:** Accepted (2026-06-27, PRs #45 & #47, issues #16 & #17)

## Context
The frontend shipped `ng serve` (the dev server) as production and fetched
from a hardcoded `http://localhost:5000`, which is cross-origin (needs CORS)
and not portable across environments.

## Decision
- Build the app with a multi-stage Docker image and serve the static bundle
  from a pinned `nginx:1.27-alpine`.
- The API base URL comes from `src/environments/environment*.ts`: dev →
  `http://localhost:5000/api/sensors`; prod → relative `/api/sensors`.
- nginx serves the SPA (`try_files … /index.html`) and reverse-proxies
  `/api` to `backend:5000`, so in production the browser stays on a single
  origin and **no CORS is involved**.

## Consequences
- Production needs no CORS for the app's own calls; `CORS_ORIGINS` remains
  for any direct cross-origin access (defense in depth).
- nginx resolves `backend` at startup; `depends_on: condition:
  service_healthy` guarantees the backend is up first. If the backend
  container is later recreated with a new IP, nginx needs a reload — a
  `resolver` + variable is the robust fix if that becomes a problem.
- For non-compose deploys (e.g. Render, #29) the proxy target / API URL must
  be configured for that topology.
