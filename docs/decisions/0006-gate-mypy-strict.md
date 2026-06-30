# ADR-0006 — Gate `mypy --strict` on the backend

**Status:** Accepted (2026-06-30, issue #61). Supersedes the mypy carve-out in
[ADR-0002](0002-ci-gates-green-subset.md).

## Context
ADR-0002 shipped CI as a deliberately green subset and deferred `mypy --strict`
because the backend was unannotated and `db.Model` / `flask_migrate` typed as
`Any`. CLAUDE.md §2.2/§3.2 target a strict-clean backend, so the carve-out was
always meant to be temporary.

## Decision
- Annotate every backend signature and gate `mypy --strict` (`mypy src` from
  `backend/`, config in `pyproject.toml`) in CI and as a pre-commit hook.
- **Typed model base.** Define an explicit `class Base(DeclarativeBase)` in
  `extensions.py` and construct `SQLAlchemy(model_class=Base)`. Models subclass
  `Base` **directly** (not `db.Model`, which flask-sqlalchemy still types as
  `Any`) and declare columns with `Mapped[...]` / `mapped_column`, so instance
  attributes carry real types (`SensorData.id` is `int`). An explicit
  `__tablename__` preserves the table name without relying on the base's
  auto-naming. This is schema-compatible — no migration change.
- **Untyped third-party libs.** `flask_migrate` and `flask_cors` ship no types;
  silence their missing-import error with a scoped `[[tool.mypy.overrides]]`
  rather than weakening strictness for our own code.

## Consequences
- New backend code must be annotated or CI fails — the type boundary is now
  enforced, not aspirational.
- The CI job retains the name **"Backend (ruff + pytest)"** even though it now
  also runs mypy, because that string is a required status check in branch
  protection; renaming it would block merges until the protection rule is
  updated. Rename + update protection together as a follow-up if desired.
- The `Mapped` model style is the SQLAlchemy 2.0 idiom; future models should
  follow it.
