# Playbook

Operational commands and workflows for `sensor_app`. (This is a focused
starter; broader workflows are expanded in #26.)

## Local quality gates (pre-commit)

Layer-2 gates (CLAUDE.md §3.2) mirror CI and run before each commit, so
problems are caught locally before they are pushed.

Install once per clone:

```bash
pip install pre-commit
pre-commit install          # enable the git hook
cd frontend && npm ci       # the eslint/prettier hooks use this toolchain
```

Run manually:

```bash
pre-commit run --all-files  # every hook across the whole repo
pre-commit run ruff-check   # a single hook
pre-commit autoupdate       # bump pinned hook versions
```

Hooks (see [`.pre-commit-config.yaml`](../.pre-commit-config.yaml)):

| Hook | Scope | Mirrors CI |
| --- | --- | --- |
| `ruff-check` | `backend/` Python lint | `ruff check backend` |
| `gitleaks` | secret scan | gitleaks job |
| `eslint` | `frontend/` TS/HTML lint | `npm run lint` |
| `prettier` | `frontend/src` format check | `npm run format:check` |
| `check-yaml`, `check-merge-conflict`, `check-added-large-files` | repo | — |

> **mypy is not enabled yet.** The backend is not fully type-annotated and
> `db.Model` / `flask_migrate` need typing work first — the same reason CI
> defers `mypy --strict`. A mypy hook joins once the annotations land.
