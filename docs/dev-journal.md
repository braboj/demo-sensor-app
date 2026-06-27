# Dev Journal

A session-by-session log of significant work. Newest entry first.

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
