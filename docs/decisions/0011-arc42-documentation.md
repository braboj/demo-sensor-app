# ADR-0011 — arc42 architecture documentation

**Status:** Accepted (2026-07-02, issue #10)

## Context
The project needs a standard, navigable architecture reference grounded in the
code. Issue #10 asked to document the product (C4 or arc42) and originally also
to generate a static web page with MkDocs and deploy it to GitHub Pages.

The reference set already exists as plain Markdown — the README, ONBOARDING,
PLAYBOOK, DEPLOY, the dev journal, and the ADRs under `docs/decisions/` — all of
which render directly on GitHub with no build step. A generated documentation
site would add a toolchain and a publish workflow to keep in sync with the code,
for a reference that reads fine as Markdown. The sibling project
`braboj/demo-randomgen` made the same call in its
[AD-10](https://github.com/braboj/demo-randomgen/blob/main/docs/decisions/010-arc42-documentation.md).

## Decision
Document the architecture with the **arc42** template — the twelve chapters under
[`docs/arc42/`](../arc42/) — written so each chapter builds on the previous ones
without assuming detail introduced later, so the set also reads as a tutorial.

The **static-site and GitHub Pages scope of #10 is dropped**: no `mkdocs.yml`, no
generated pages, and no Pages workflow. The docs are Markdown with Mermaid
diagrams, cross-linked to the code.

arc42 §9 ([`09-architecture-decisions.md`](../arc42/09-architecture-decisions.md))
is the index of these ADRs.

## Alternatives considered
- **C4 model** — rejected in favor of arc42, which carries the prose sections
  (constraints, runtime, deployment, crosscutting concepts, quality, risks) that
  make the set usable as a step-by-step tutorial, not only a set of diagrams.
- **MkDocs documentation site + GitHub Pages** — rejected; a build step plus
  generated pages to keep in sync, for a reference that renders fine as Markdown
  on GitHub.

## Consequences
- Each arc42 section is one Markdown file with Mermaid diagrams, cross-linked to
  the code and the other hand-written docs.
- No build or publish step; the docs render on GitHub as-is.
- Each new ADR is added both to arc42 §9 and to the
  [decisions README](README.md).
