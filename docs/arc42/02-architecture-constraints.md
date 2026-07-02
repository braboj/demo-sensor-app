# 2. Architecture Constraints

Constraints are fixed conditions the architecture must respect. They come from
the technology stack, the project's conventions, and the nature of a small,
hosted, multi-service demo.

## 2.1 Technical constraints

Technical constraints fix the languages, frameworks, and runtime shape the
system is built on.

| ID | Constraint |
|------|------------|
| T01 | The backend is built on Python 3.12 and the Flask web framework, served in production by a WSGI server (never the Flask development server). |
| T02 | The frontend is an Angular 19 single-page application written in TypeScript with strict mode enabled. |
| T03 | PostgreSQL is the system of record. The backend reaches it through the SQLAlchemy ORM, and every schema change ships as a reversible migration rather than being created at runtime. |
| T04 | The system runs as four separate services — backend, frontend, database, and dashboard — each its own container image, orchestrated together. |
| T05 | Third-party dependencies are limited to free, open-source software. |
| T06 | The hosted demo must fit a zero-cost, free-tier platform: limited memory, shared CPU, and no guarantee of an always-on background process. |

## 2.2 Organizational and convention constraints

Organizational and convention constraints fix the project's process and coding
conventions.

| ID | Constraint |
|------|------------|
| O01 | Code must pass the automated quality gates — linting, type checks, and test coverage — before it merges. |
| O02 | The backend is fully type-annotated and passes a strict type check; code raises specific, named errors rather than generic ones. |
| O03 | Work happens on branches through pull requests; the `main` branch is protected and requires a green CI run and an approval before merge. |
| O04 | Commits follow Conventional Commits. |
| O05 | Significant architectural decisions are recorded as Architecture Decision Records; this documentation is the architecture reference. |

## 2.3 Security and runtime constraints

Security and runtime constraints fix how the services are run and kept safe.

| ID | Constraint |
|------|------------|
| S01 | No service runs with debug mode enabled in production, and no development server ships in any image. |
| S02 | The repository holds no secrets; every secret and environment-specific value is supplied at runtime through environment variables. |
| S03 | Cross-origin access from the browser is scoped to the configured frontend origin — never a wildcard. |
| S04 | The backend binds the port the hosting platform provides and serves plain HTTP; the platform's edge terminates TLS. |
| S05 | All input is validated at the boundary: a bad query parameter is rejected with an HTTP 400 rather than silently falling back to a default. |
