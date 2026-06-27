# ADR-0002 — CI gates only currently-green checks; strict gates phase in

**Status:** Accepted (2026-06-27, PR #32, issue #19)

## Context
The target convention (CLAUDE.md §3.2) calls for backend `ruff + mypy +
pytest`, frontend `lint + build + test`, gitleaks, and CodeQL — with "no
allowed-to-fail stages". But on the current MVP code, three of those would
land **red** immediately: `mypy --strict` reports 62 errors (the backend is
unannotated), there is no ESLint config, and there was no Karma test target.

## Decision
Gate only what passes today and phase the rest in as their prerequisite
issues land, each marked with a `NOTE` in `ci.yml`:
- **Now:** backend `ruff` + `pytest`, frontend `npm ci` + `build`, gitleaks,
  CodeQL (python + js-ts), Dependabot (pip/npm/actions).
- **Frontend tests:** added in #18 (Karma).
- **Deferred:** `mypy --strict` → after the backend is annotated (#24);
  frontend ESLint → after the config lands (#25).

We chose green-and-narrow over broad-and-red rather than using
`continue-on-error` (which would violate "no allowed-to-fail stages").

## Consequences
- CI is trustworthy from day one: a red check means a real regression.
- Coverage is intentionally incomplete; the gaps are explicit (in-file
  `NOTE`s + the dev journal) so they are not mistaken for "covered".
- Each deferred gate is a one-line addition when its issue closes.
