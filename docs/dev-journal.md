# Dev Journal

A session-by-session log of significant work. Newest entry first.

---

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
- Triaged + merged 10 Dependabot PRs (#35–#44: CI action bumps, flask-cors 5→6,
  pytest 8→9, ruff 0.8→0.15).
- Configured branch protection on `main` (required checks + up-to-date + PR +
  1 approval; admins not enforced so the owner merges via override); enabled
  repo auto-merge + delete-branch-on-merge.

### Known follow-ups / not verified this session
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

---

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
- Data generator runs as a dedicated worker process, not a factory thread — **ADR-0001**.
- CI gates only currently-green checks; `mypy --strict` (#24) and frontend ESLint (#25) phase in later — **ADR-0002**.
- Production frontend served by nginx with a same-origin `/api` proxy (no CORS in prod) — **ADR-0003**.

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
unblocks mypy-strict gate), #25 (frontend polish → unblocks ESLint gate),
#26 (docs reconcile + ONBOARDING/PLAYBOOK), #27 (pre-commit hooks).
