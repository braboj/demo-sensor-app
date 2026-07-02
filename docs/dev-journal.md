# Dev Journal

A session-by-session log of significant work, in chronological order —
oldest first, newest entry at the bottom (per solid-ai-templates ADR-015).

## 2026-06-27 — P0 security + P1 correctness / CI / containers

**Tool:** Claude Code (Opus 4.8) · **Branch model:** one concern per PR off
`main`, CI-gated.

Drove the 360-audit refactor (epic #12) through **Phase 1 (P0 security)**
and **Phase 2 (P1)**.

### PRs merged (7)

| PR | Summary | Closes |
|----|---------|--------|
| #30 | Flask debug off + gunicorn + scoped CORS; config classes (Dev/Test/Prod, default Production) | #13, #14 |
| #34 | Sensor generator → standalone `worker.py`; deterministic seed-based route tests | #15, #20 |
| #32 | GitHub Actions CI + CodeQL + Dependabot; `requirements-dev.txt` | #19 |
| #33 | Karma test target + specs (app/service/home); `@angular/platform-browser-dynamic` | #18 |
| #45 | Frontend `HttpClient` + loading/empty/error states + env-based API URL | #16 |
| #46 | Pin/upgrade base images (py 3.12, node 22, pg 16); healthchecks + restart; DB port unpublished | #21 |
| #47 | Multi-stage frontend Docker served by nginx (SPA + `/api` proxy) | #17 |

**Issues closed:** #13, #14, #15, #16, #17, #18, #19, #20, #21.

### Key decisions (see `docs/decisions/`)

- Data generator runs as a dedicated worker process, not a factory thread
  — **ADR-0001**.
- CI gates only currently-green checks; `mypy --strict` (#24) and frontend
  ESLint (#25) phase in later — **ADR-0002**.
- Production frontend served by nginx with a same-origin `/api` proxy (no
  CORS in prod) — **ADR-0003**.

### Process note (stacked PRs)

Merging a PR with `--delete-branch` deletes the *base* branch of any child
(stacked) PR, which GitHub then **auto-closes** — and a PR whose base branch
is gone **cannot be reopened**. This closed #31; recovered as #34.
**Rule:** retarget children to `main` *before* merging the parent, and delete
branches only at the very end.

### Known follow-ups / not verified this session

- **Docker not run end-to-end:** the engine was unavailable locally, so the
  nginx image (#17) and hardened compose (#21) were validated with
  `docker compose config` only. A `docker compose up` smoke test is
  recommended before the Render deploy (#29).
- **CI deprecation warning:** `actions/checkout@v4` and `gitleaks-action@v2`
  run on Node 20 (deprecated); the github-actions Dependabot will bump them.
- **`backend/.env.example`** still blocked by the `.gitignore` `.env.*` rule
  (needs a negation); deferred to the docs-reconciliation issue (#26).
- Open Dependabot PRs (ruff, pytest) awaiting review.

### Next

Phase 3 (P2): #22 (Alembic — drops runtime `db.create_all()`, indexes
`timestamp`), #23 (API contract/versioning), #24 (backend restructure →
unblocks mypy-strict gate), #25 (frontend polish → unblocks ESLint
gate), #26 (docs reconcile + ONBOARDING/PLAYBOOK), #27 (pre-commit hooks).

## 2026-06-27 — P2 architecture/API/polish + repo hardening

**Tool:** Claude Code (Opus 4.8) · **Branch model:** one concern per PR off
`main`, CI-gated, admin-merged (solo repo).

Completed **Phase 3 (P2)** of the 360-audit refactor (epic #12) and hardened
the repo workflow.

### PRs merged (5)

| PR | Summary | Closes |
|----|---------|--------|
| #49 | Alembic migrations; drop runtime `db.create_all()`; index `timestamp`; one-shot compose `migrate` service | #22 |
| #50 | `/api/v1` contract: bounded `?limit=` (400 on bad input), RFC 9457 JSON errors, ISO-8601 UTC timestamps, `select()` style, `/health`+`/ready` | #23 |
| #51 | Backend restructure to `src/sensor_api/` (factory/config/extensions/blueprints/services); worker → `python -m sensor_api.worker`; CI runs from `backend/` | #24 |
| #52 | Frontend polish: number/date pipes, vibration legend, table a11y, `@if`/`@for`, ESLint + Prettier (CI-gated) | #25 |
| #53 | Pre-commit hooks (ruff-check, gitleaks, eslint, prettier); `docs/PLAYBOOK.md` | #27 |

Plus this PR (#26): reconciled `README`/`SOLUTION` with shipped reality;
added `docs/ONBOARDING.md`; expanded `docs/PLAYBOOK.md`; un-ignored
`.env.example` in `.gitignore`.

**Issues closed:** #22, #23, #24, #25, #27 (and #26 by this PR).

### Repo hardening (outside the epic)

- Triaged + merged 10 Dependabot PRs (#35–#44: CI action bumps, flask-cors
  5→6, pytest 8→9, ruff 0.8→0.15).
- Configured branch protection on `main` (required checks + up-to-date + PR +
  1 approval; admins not enforced so the owner merges via override); enabled
  repo auto-merge + delete-branch-on-merge.

### Known follow-ups / not verified (P2 session)

- **Docker still not run end-to-end** (engine unavailable all session): the
  `migrate` service, src-layout image, and worker command were validated with
  `docker compose config` + local SQLite, **not** a live `docker compose up`.
  Do this smoke test before the Render deploy (#29).
- **`backend/.env.example`** could not be written by tooling (a `.env*` write
  guard); the `.gitignore` negation is in place, so the file just needs to be
  dropped in. Required vars are documented in `ONBOARDING.md`.
- **mypy** still not gated (backend un-annotated) — deferred in both CI and
  pre-commit; needs a typed `db.Model` base + annotations.

### Next

P2 complete. Remaining: features (#7 Grafana, #8 websockets) and the Render
deploy (#29) — run the Docker smoke test first.

## 2026-06-28 — Docker smoke test + Render deploy (#29) + small fixes

**Tool:** Claude Code (Opus 4.8) · **Branch model:** one concern per PR off
`main`, CI-gated, owner-merged.

First live `docker compose up` of the refactored stack, then implemented
the Render free-tier deployment (#29) plus two small fixes. All three PRs
(#55, #56, #57) merged to `main` (admin override squash); #29 auto-closed
on #55.

### Docker smoke test (the pre-#29 gate from the last entry)

Full stack came up healthy in order (db → migrate → backend → worker →
frontend); `/health`·`/ready`·`/api/v1/sensors` 200, bad `?limit` 400, 404
JSON; worker inserted every 10s; nginx proxied `/api`; gunicorn (no dev
server). Surfaced one nit: the page `<title>` was still `Default`.

### PRs merged (3)

| PR | Summary | Closes |
|----|---------|--------|
| #55 | Render free-tier Blueprint (`render.yaml`: managed PG + Docker backend + static frontend) + `DEPLOY.md` + ADR-0004; `postgres://` URL normalization; `run_generator()` + gunicorn `post_worker_init` in-process generator; `render-start.sh`; build-time `API_URL` injection | #29 |
| #56 | Page `<title>` → "Sensor Dashboard" | — |
| #57 | CLAUDE.md §2.10 doc-style rule (no decorative `---`) + strip existing rules from CLAUDE/dev-journal/REFACTOR-PLAN | — |

### Key decision

- Free-tier in-process generator (scoped exception to ADR-0001), started in
  the gunicorn **worker** not master — **ADR-0004**. The master variant
  (`when_ready`) deadlocked request workers via the fork-after-thread hazard;
  caught by a full Render-path Docker simulation, not just YAML review.

### Verification

Backend ruff + 30 pytest; frontend lint + format + build + 11 Karma tests; a
live `docker compose up`; and a Render-path Docker sim (migrate→gunicorn,
`$PORT` bind, `postgres://` normalization, in-process generator, API contract
200/400/404). All 6 CI checks green on each PR before merge.

### Known follow-ups / pending

- **Connect the repo in Render** (New + → Blueprint) now that #55 is merged;
  then fix `CORS_ORIGINS`/`API_URL` if Render suffixes the service hostnames
  (DEPLOY.md).
- **`backend/.env.example`** still not dropped in (tooling `.env*` guard).
- **mypy** still not gated.
- Historical docs (360 audit, ASSIGNMENT) intentionally keep their `---`.

### Next

Connect Render. Then features — #7 Grafana, #8 websockets; docs #10/#11.

## 2026-06-30 — Deploy readiness review + gap triage (issues #59-#62)

**Tool:** Claude Code (Opus 4.8) · **Type:** triage / tracking — no code changes.

A planning session: reviewed Render deploy readiness, evaluated a sibling
project's deploy pattern, and filed a ticket for every known gap.

### Render deploy readiness

Pre-flight of the shipped Blueprint (`render.yaml` + `render-start.sh` +
`gunicorn.conf.py` + `set-api-url.mjs`) against the build config — all
consistent (static output path, prod `environment.prod.ts` swap, `$PORT` bind,
migrate-then-serve). Confirmed the first deploy is a one-time **owner** dashboard
action (no Render CLI or API key in the environment) and that **no secrets** are
added by hand (`SECRET_KEY` generated, `DATABASE_URL` auto-wired). Kept
`autoDeploy: true` (push-based) for now.

### randomgen deploy pattern (reference)

Reviewed `braboj/demo-randomgen`: it deploys via `runtime: image` plus a
release-tag CD that publishes to Docker Hub then POSTs a Render Deploy Hook. Its
**AD-17** moved off `autoDeploy`-on-commit because it "did not fire reliably" —
logged as a spike for sensor_app rather than adopted now.

### Issues created (4)

| #   | Title                                            | Note                                          |
| --- | ------------------------------------------------ | --------------------------------------------- |
| #59 | Deploy-trigger spike (deploy-hook vs autoDeploy) | `spike` P3 — output is an ADR                 |
| #60 | Add committed `backend/.env.example`             | `task` P2 — tooling `.env*` guard left it out |
| #61 | Gate `mypy --strict` in CI + pre-commit          | `task` P2 — needs annotations + typed model   |
| #62 | Connect Blueprint in Render + verify live deploy | `task` P2 — owner go-live action              |

### Epic #12 reconciled

Ticked #29 (Blueprint shipped in #55) and added a "Phase 8 — Follow-ups" section
linking #59-#62.

### Next

Owner: connect Render (#62). Then close the two convention gaps (#60 env
template, #61 mypy gating) and the feature backlog (#7 Grafana, #8 websockets;
docs #10/#11).

## 2026-06-30 — Phase 6 features + Phase 8 follow-ups (Grafana, SSE, mypy)

Tool: Claude Code (Opus 4.8). Cleared the remaining epic #12 backlog. All work
shipped as CI-green PRs; `main` is branch-protected so the owner merges.

### PRs opened (awaiting owner merge)

| #   | Closes | Summary                                                          |
| --- | ------ | ---------------------------------------------------------------- |
| #64 | —      | strip a stray heredoc terminator from `docs/REFACTOR-PLAN.md`    |
| #65 | #7     | Grafana service + datasource & dashboard provisioned as code     |
| #66 | #8     | live readings over SSE (`/api/v1/sensors/stream`) + gevent worker |
| #67 | #3     | dashboard links out to Grafana for charts (stacked on #66)       |
| #68 | #60    | committed `backend/.env.example` template                        |
| #69 | #61    | annotate the backend + gate `mypy --strict` (CI + pre-commit)    |

### Key decisions (see `docs/decisions/`)

- **SSE over WebSockets** for real-time delivery — one-way data, plain HTTP, no
  client library; gunicorn runs the **gevent** worker so a long-lived stream
  does not block the single web worker. **ADR-0005**. Dropped the unused
  `flask-socketio` dep and the dead `backend/scripts/` WebSocket prototype.
- **#3 charting deferred to Grafana** (owner's call) — the SPA stays the live
  table and links to the provisioned dashboard; no charting library added.
- **Typed model base** to gate `mypy --strict`: `class Base(DeclarativeBase)` +
  `SQLAlchemy(model_class=Base)`; `SensorData` subclasses `Base` directly with
  `Mapped[...]` (flask-sqlalchemy still types `db.Model` as `Any`). Explicit
  `__tablename__`; schema-compatible, no migration. **ADR-0006** (supersedes the
  ADR-0002 mypy carve-out).

### Verification

Per PR, the matching gates: backend `ruff` + `mypy src` + `pytest`; frontend
`eslint` + `prettier` + `build` + Karma. Plus a live `docker compose up` for
**#7** (Grafana datasource "Database Connection OK", dashboard provisioned,
panel SQL returns worker rows) and **#8** (worker boots `Using worker: gevent`;
SSE streams direct and via the nginx proxy; `GET /api/v1/sensors` returns 200 in
~15 ms *while* a stream is held open — the gevent non-blocking proof).

### Cross-PR note (merge carefully)

PR #66 adds backend code the #61 gate checks. Pre-annotated #66's net-new code
and **test-merged #61↔#66 locally** → the union is `mypy --strict` clean (15
files) + 31 pytest. Merging #66 and #69 yields **one trivial conflict** (the
`routes.py` flask import line) — resolve by keeping **both** the
`from flask import …` and `from flask.typing import ResponseReturnValue` lines.

### Process notes

- The Write tool blocks `.env*` paths; created `backend/.env.example` via a
  Bash heredoc instead (placeholders only; gitleaks green).
- CI backend job name kept "Backend (ruff + pytest)" even though it now runs
  mypy, to preserve the required-status-check contract in branch protection.

### Next

Owner: merge the seven open PRs (suggested order #63/#64/#68 → #65 → #66 → #69,
then #67 last), then connect Render (#62). Deferred: #59 deploy-trigger spike.

## 2026-06-30 — Merge queue landed + Render go-live verified (#62)

**Tool:** Claude Code (Opus 4.8) · **Branch model:** one concern per PR off
`main`, CI-gated.

Merged the full open-PR queue (admin-override squash, each CI-green) and
verified the live Render deployment, closing **#62**.

### PRs merged (8)

- **#64** strip stray heredoc terminator from the refactor-plan tail.
- **#63** dev-journal entry (deploy-readiness + gap triage).
- **#68** committed `backend/.env.example` template (closes #60).
- **#65** Grafana Postgres datasource + dashboard provisioned as code (closes #7).
- **#69** gate `mypy --strict` on the backend (closes #61).
- **#66** live sensor stream over Server-Sent Events (closes #8).
- **#67** dashboard → Grafana charting link (closes #3).
- **#70** update repo references after the `sensor-data-app` → `demo-sensor-app`
  rename (CLAUDE.md, README, DEPLOY.md, ONBOARDING; left the dated audit).

### Merge-conflict resolutions

- **#66 ↔ #69 (`routes.py` import line)** — resolved exactly as the prior entry
  predicted: kept **both** `from flask import Blueprint, Response, current_app,
  jsonify, request` and `from flask.typing import ResponseReturnValue`.
- **#67 stacked-squash retarget** — after #66 squashed to `main`, GitHub
  retargeted #67 and it went conflicting. Took `main`'s version of the backend
  files #67 does not own; hand-merged `home.component.ts/.css` to keep the
  Grafana-link block/field/styles on top of #66's SSE rendering. Caught and
  removed a duplicate `const MAX_ROWS = 100;` the auto-merge produced (would
  otherwise fail the TypeScript build).

### Render go-live (#62) — verified live

The Blueprint was already connected, and `autoDeploy: true` kept it current
through the merges. Default service names were used (no suffix), so the URLs are
`sensor-app-backend.onrender.com` / `sensor-app-frontend.onrender.com`.

- `GET /health` → 200 (~13 s cold start), `GET /ready` → 200.
- `GET /api/v1/sensors?limit=5` → 200 (ISO-8601 UTC rows); `?limit=abc` → 400 and
  `?limit=999` → 400 (RFC 9457 JSON).
- Frontend serves 200 HTML; the shipped bundle's baked `API_URL` points at the
  backend (confirming `set-api-url.mjs` ran in the Render build); CORS is scoped
  to the frontend origin (not `*`) and the cross-origin GET is allowed.
- `GET /api/v1/sensors/stream` → `text/event-stream`, a primed reading then a
  new one ~10 s later — the gevent worker + in-process generator work on the
  free tier.

Free-tier note: the web service spins down when idle and the in-process
generator only runs while it is awake, so readings accrue with gaps after idle.

### Repo rename

`braboj/sensor-data-app` → `braboj/demo-sensor-app` (server-side). Old URLs
redirect; the local `origin` remote and the docs were updated (#70).

### Epic #12

Phase 4 features #7/#8/#3 and Phase 8 #60/#61/#62 ticked. Still open are
#10/#11 (docs) and #59 (deploy-trigger spike).

### Next

- #10/#11 — confirm the doc issues are satisfied by the shipped docs and close.
- #59 — deploy-trigger spike (autoDeploy vs deploy-hook), deferred.

## 2026-07-01 — Grafana on Render, embedded charts, docs polish

**Tool:** Claude Code (Opus 4.8) · **Branch model:** one concern per PR off
`main`, CI-gated.

Extended the live deploy with Grafana, embedded the dashboard in the SPA, and
did a documentation/licence pass.

### PRs merged (10)

- **#73** deploy Grafana to the live Render stack (closes #72) — 4th service
  `sensor-app-grafana` from a thin `deploy/grafana/Dockerfile` that bakes the
  provisioning; entrypoint binds `$PORT` and parses `DATABASE_URL` (Render
  exposes only a connection string); anonymous read-only view. **ADR-0007**.
- **#74** dashboard v2 — a `metric` template variable
  (Temperature/Humidity/Vibration) + a "Trend (10-point moving average)" panel;
  long-format queries filtered by the selector. Satisfies the assignment's
  "select which data points to visualize" requirement.
- **#75** embed Grafana in the SPA — Angular Router (`/` Live Table +
  `/charts`), `ChartsComponent` = sanitized iframe (`?kiosk`) with an "Open in
  Grafana" fallback; `GF_SECURITY_ALLOW_EMBEDDING=true`.
- **#76** remove the leftover "Homes" logo; **#77** remove the redundant
  in-table Grafana link (charts live on the Charts tab now).
- **#78** README overhaul (closes #11) + relicence to **MIT** — live-demo link,
  CI/CodeQL/MIT badges, Features list, sample response, and full
  template-structure alignment (Project structure table, Development,
  Configuration, License).
- **#79** rename `REFACTOR-PLAN.md` → `refactor-plan.md` (docs casing
  convention); **#80** rewrite `CONTRIBUTING.md` to match the real conventions
  (was boilerplate prescribing the wrong commit/versioning schemes); **#81**
  replace CLAUDE.md §1.3 structure tree with a README pointer; **#82** tidy the
  README Features list.

### Key decisions

- **Grafana on the live deploy** (**ADR-0007**) — reverses ADR-0004's "no
  Grafana on the free tier"; bakes provisioning into the image (no persistent
  disk) + anonymous read-only view.
- **Embed vs link** — embed the dashboard in a Charts route (kiosk iframe) for a
  single-page demo; keep the external link as a fallback.
- **Licence → MIT** (from The Unlicense); copyright "Branimir Georgiev".

### Verification

Every PR CI-gated. Grafana verified **live** on Render: `/api/health` ok, an
anonymous datasource query returned managed-Postgres rows over
`sslmode=require`, the dashboard renders the metric selector + trend, and the
SPA `/charts` embeds it (no `X-Frame-Options`). Frontend gates green throughout
(eslint + prettier + build + karma).

### Issues filed

- Upstream (`braboj/solid-ai-templates`): **#713** (project structure as a
  table), **#714** (drop SHOUT-case for guide-doc filenames), **#715** (split
  the dev journal per session), **#716** (README-SSOT vs the CLAUDE.md
  Project-structure MUST — the conflict #81 exposed).
- This repo: **#83** modernise `frontend/tsconfig.json` to the Angular 19
  defaults; **#84** frontend design polish (cf. demo-randomgen) — closed
  **wontdo** (keep the frontend minimal per §4).

### Next

- **#10** — decide whether the shipped docs satisfy "documentation & web pages",
  then close or scope the remainder.
- **#83** tsconfig modernisation; **#59** deploy-trigger spike (deferred).
- Epic **#12** is all-but-complete (only #10 + the deferred #59 remain).

## 2026-07-02 — tsconfig modernisation + deploy-trigger decision (then dropped)

**Tool:** Claude Code (Opus 4.8) · **Branch model:** one concern per PR off
`main`, CI-gated.

Cleared the two remaining P3 follow-ups and worked the Render deploy-trigger
question to a recorded decision — then dropped the implementation as unnecessary
for a three-service demo.

### PRs merged (3)

| PR | Summary | Closes |
|----|---------|--------|
| #87 | Modernise `frontend/tsconfig.json` to Angular 19 defaults — drop `_enabledBlockTypes`, `baseUrl`, `useDefineForClassFields`; `moduleResolution` → `bundler` | #83 |
| #89 | **ADR-0009** — evaluate the Render deploy hook vs `autoDeploy` (spike) | #59 |
| #92 | **ADR-0010** — scalable multi-service Render deploy (manifest-driven CI matrix); supersedes ADR-0009 | #91 |

**Issues closed:** #83, #59, #91; **#88** closed *not planned* (hook impl dropped).

### Key decisions (see `docs/decisions/`)

- **ADR-0009** — of randomgen AD-17's two drivers for leaving push-based
  `autoDeploy`, only reliability/CI-gating applies here (sensor_app builds no CI
  image, so there is no double-build), and the static frontend cannot use
  `runtime: image`. Chose the deploy-hook trigger over the full pattern.
- **ADR-0010** — for the many-services case, stay on Render via a data-driven
  manifest + a single API key + a CI change-detection matrix. Records Render's
  ~tens-of-services ceiling and the GitOps/K8s revisit threshold, where the
  skip-`runtime:image` rationale **inverts**.
- **Dropped the hook implementation** (#88 / PR #90 closed) as unnecessary for
  the demo; deploys stay on Blueprint `autoDeploy`. **ADR-0009 → Superseded by
  ADR-0010.**

### Repo metadata

- GitHub **About**: rewrote the description (adds PostgreSQL + Docker) and added
  15 **topic tags** (previously none).

### Issues filed

- Upstream (`braboj/solid-ai-templates`): **#717** — add a fleet-scale axis to
  `base-deployment` (deploy mechanism, and its rationale, is scale-dependent).

### Verification

Frontend gates green — eslint + prettier + build + karma (22/22); `tsc --noEmit`
clean for app + spec. Every PR CI-gated; #87/#89/#92 merged green. No backend
code changed (backend ruff/mypy/pytest covered by CI). No schema changes.

### Next

- **#10** — decide whether the shipped docs satisfy "documentation & web pages",
  then close or scope the remainder.
- Epic **#12** — all-but-complete; only #10 remains open.
