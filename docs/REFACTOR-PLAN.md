# Refactoring Plan — sensor_app → production-shaped solution

Tracking epic: [#12](https://github.com/braboj/demo-sensor-app/issues/12).
Target conventions: [`CLAUDE.md`](../CLAUDE.md). Gap source: the 360 audit
at [`docs/audits/2026-06-26-360.md`](audits/2026-06-26-360.md) (overall
**D**; 2 Critical, 39 High+).

## Goal

Transform the working MVP take-home into a maintainable, secure,
testable multi-service app (Flask API + Angular SPA + PostgreSQL +
Grafana) that matches the `CLAUDE.md` target, without changing the
product's user-facing purpose. Success = the next 360 grades the
engineering dimensions at **A-/B+** with zero Critical/High findings.

## Current state (post-cleanup)

- **Done already** (cleanup/restructure pass): removed `frontend.zip`,
  `.tutorial/`, `db.json`, orphan `.pyc`, dead npm deps; added
  `.dockerignore` (both) + committed lockfile + `npm ci`; relocated the
  templates submodule to `docs/solid-ai-templates/`; moved docs into
  `docs/{audits,history}`; fixed README links; renamed app identity;
  added `pyproject.toml` pytest bootstrap; generated `CLAUDE.md`.
- **Still as-is:** backend runs the Flask dev server with `debug=True`,
  wildcard CORS, a generator thread inside `create_app()`,
  `db.create_all()` at runtime, old `app/` layout; frontend uses `fetch`
  + hardcoded URL with no error states; no migrations; no CI; EOL base
  images.

## Sequencing principles

1. **Security first** — land the P0 fixes before anything else.
2. **Backbone before detail** — restructure the backend once, then layer
   API/DB/worker changes onto the new shape (avoid double-work).
3. **Make it testable before automating** — tests must run from a clean
   clone before CI is wired (CI gates on green tests).
4. **Package last** — finalize Docker/compose after app behavior is
   stable.
5. **One concern per PR**, each closing its issue; run the gates after
   every change.

## Dependency graph (high level)

```
#13 #14  (P0, standalone)
        \
#24 ── restructure backbone ──┬── #23 API contract
                              ├── #22 migrations
                              └── #15 worker
#20 backend tests ────────────┘
#16 frontend core ── #25 polish ── #18 frontend tests
#18 + #20 ──► #19 CI ──► (#27 pre-commit mirrors CI hooks)
app stable ──► #21 compose/images, #17 frontend image
all above ──► #26 docs reconcile + companions
stable base ──► #7 Grafana, #8 real-time, #3 (features)
```

---

## Phase 1 — Security (P0) · issues #13, #14

Smallest possible diffs on the current code for immediate risk
reduction; carried forward through the restructure.

- **#13** `debug=False`; introduce config classes' `DEBUG` flag; switch
  the container `CMD` to `gunicorn "...:create_app()"`; add `gunicorn`
  to requirements.
- **#14** Replace `CORS(app)` with origins from `CORS_ORIGINS` env.

**Done when:** no debugger/dev-server in the image; CORS not `*`; app
still boots via `docker compose up`.

## Phase 2 — Backend backbone & correctness (P1/P2) · #24 → #22, #23, #15, #20

Do `#24` first; the rest build on the new structure.

- **#24** Restructure to `backend/src/sensor_api/` (factory, `config.py`
  with Dev/Test/Prod, `extensions.py`, `blueprints/{sensors,health}/`,
  `services.py`, `errors.py`). Thin routes; services own logic.
- **#22** Add Flask-Migrate (Alembic); remove runtime `db.create_all()`;
  index `SensorData.timestamp`.
- **#23** Harden the API: bounded `limit` (400 on non-int), JSON error
  handlers, ISO-8601 timestamps, `/api/v1` prefix, `/health` + `/ready`.
- **#15** Move the generator to `sensor_api/worker.py` (own context +
  session, per-insert rollback); add a `worker` service to compose.
- **#20** Update tests to the new layout; seed data directly (no
  `time.sleep`); restore commented-out validation assertions; ensure
  `pytest` passes from repo root.

**Done when:** `pytest && mypy src/ --strict` green; API matches the
`CLAUDE.md` §2.4 contract; generator runs as its own service.

## Phase 3 — Frontend (P1/P2) · #16 → #25, #18 → #17

- **#16** Switch `SensorService` to `HttpClient` + `catchError`; base URL
  from `environments/environment*.ts`; loading/empty/error states; load
  in `ngOnInit`; add polling via `interval()`.
- **#25** `number`/`date` pipes; vibration legend; table a11y
  (`<caption>`, `scope`); decorative `alt=""`; add ESLint + Prettier.
- **#18** Add a real Karma `test` target + `npm test`; fix/replace the
  broken spec; add `SensorService`/`HomeComponent` specs.
- **#17** Multi-stage Dockerfile: `npm ci` + `ng build` → pinned nginx
  serving `dist/sensor-app` (no `ng serve` in prod).

**Done when:** `npm run build && npm test` green; UI handles
backend-down gracefully; production image serves static assets.

## Phase 4 — Infra, CI & gates (P1/P2) · #21, #19, #27

- **#21** Pin/upgrade images (Python 3.12, Postgres 16, pinned Node);
  healthchecks + `restart` for all services; stop publishing 5432.
- **#19** GitHub Actions: backend (ruff + mypy + pytest), frontend
  (lint + build + test), gitleaks, CodeQL; Dependabot (pip/npm/actions);
  `permissions: contents: read`. (Depends on #20, #18 being green.)
- **#27** `.pre-commit-config.yaml` mirroring the CI hooks.

**Done when:** CI is green on a PR; pre-commit blocks bad commits;
`docker compose up` is healthy end-to-end.

## Phase 5 — Documentation (P2) · #26

- Reconcile `SOLUTION.md`/`README.md` with shipped reality (mark
  Grafana/websockets/CI status accurately).
- Generate `docs/ONBOARDING.md`, `docs/PLAYBOOK.md`, `docs/dev-journal.md`
  per the templates. Close out #10/#11.

## Phase 6 — Features (pre-existing backlog) · #7, #8, #3

Only after the base is solid:

- **#7** Grafana provisioned as code (`deploy/grafana/provisioning/`),
  datasource = PostgreSQL, dashboards as version-controlled JSON.
- **#8** Real-time delivery (WebSocket/SSE) replacing/augmenting polling.
- **#3** Round out the Angular dashboard (chart selection per the
  original assignment).

---

## Verification per phase

- Backend: `pytest && mypy src/ --strict` (+ ruff).
- Frontend: `npm run build && npm test` (+ eslint).
- Integration: `docker compose up` healthy; `curl /api/v1/sensors`,
  `/health`, `/ready`.
- After Phase 5: re-run the 360 (`base/workflow/360.md`) and store a new
  `docs/audits/YYYY-MM-DD-360.md`; target zero Critical/High.

## Suggested execution

Phases 1→6 in order. Within a phase, one PR per issue. Phases 2 and 3
can run in parallel (different stacks) once Phase 1 lands; Phase 4's #19
waits on the test issues (#20, #18).
EOF
echo "written docs/REFACTOR-PLAN.md"