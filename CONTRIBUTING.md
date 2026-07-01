# Contributing

Thanks for your interest in improving this project. The full conventions live in
[CLAUDE.md](CLAUDE.md); this is the short version.

## Workflow

1. Open an issue describing the change before you start — one concern per issue.
2. Branch off `main` (`feat/<scope>`, `fix/<scope>`, `chore/<scope>`, or
   `docs/<scope>`). `main` is protected — never commit to it directly.
3. Keep the pull request small and focused — one concern per PR.
4. CI must be green and the PR needs one approval before merge.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):
`<type>(<scope>): <summary>` — types: `feat`, `fix`, `chore`, `docs`,
`refactor`, `test`. Imperative mood, subject under 80 characters. Close issues
with a keyword (for example, `Closes #12`).

## Before you push

Run the same gates CI runs:

- Backend (from `backend/`): `pytest && mypy src --strict`
- Frontend (from `frontend/`): `npm test && npx eslint .`

CI additionally runs `ruff`, a production frontend build, `gitleaks`, and
CodeQL. See [docs/ONBOARDING.md](docs/ONBOARDING.md) for setup and
[docs/PLAYBOOK.md](docs/PLAYBOOK.md) for day-to-day commands.
