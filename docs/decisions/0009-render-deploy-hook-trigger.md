# ADR-0009 — Trigger Render deploys with a CI deploy hook, not push-based autoDeploy

**Status:** Accepted (2026-07-01, spike #59)

## Context
The Render Blueprint (`render.yaml`, shipped in #55) deploys the live stack —
managed Postgres plus three web services (`sensor-app-backend`,
`sensor-app-frontend`, `sensor-app-grafana`) — with `autoDeploy: true` on every
service. Every push to `main` triggers a Render build + deploy through Render's
GitHub webhook, **regardless of CI status**: a push that fails CI still
redeploys, and the deploy is not an observable step anywhere in the pipeline.

The sibling project `braboj/demo-randomgen` moved away from this model in its
[AD-17](https://github.com/braboj/demo-randomgen/blob/main/docs/decisions/017-render-image-deploy-hook.md).
That ADR records two first-hand drivers:

- **(a) Reliability / observability** — commit-based `autoDeploy` "did not fire
  reliably," so the demo lagged the released code, and nothing made a deploy an
  explicit step.
- **(b) Double build** — randomgen's release workflow already builds and pushes
  an image to Docker Hub, so Render was rebuilding the same artifact a second
  time. AD-17 fixed both by switching Render to `runtime: image` and POSTing a
  deploy hook on each release tag.

Two sensor_app-specific facts reshape how AD-17 applies:

- **Driver (b) does not exist here.** sensor_app's CI publishes no image and has
  no release/tagging process, so there is no CI-built artifact for Render to
  double-build. Only driver (a) — unreliable, un-gated deploys — is a real
  problem for this project.
- **The deploy surface is heterogeneous.** sensor_app has three deploy targets,
  and the **frontend is a Render static site** (Render builds it from source);
  it cannot use the `runtime: image` model at all. The backend and grafana are
  Docker services and *could* pull published images, but doing so for only two
  of three services would create a split deploy model.

## Decision
Adopt **the deploy-hook trigger, keeping Render's build** (spike Option 1):

- Set **`autoDeploy: false`** on all three web services in `render.yaml`. Render
  keeps building each service from source (backend Dockerfile, frontend static
  build, grafana Dockerfile) — no registry publishing is introduced.
- Add a **`deploy` job to `ci.yml`** that runs only on `push` to `main`, is
  gated `needs: [backend, frontend]` so a red pipeline never deploys, and POSTs
  one Render deploy hook per service. Each POST is **skipped when its secret is
  unset**, so the workflow stays green before the hooks exist and on
  forks / pull requests.
- The three deploy-hook URLs are **GitHub Actions secrets** created once in the
  Render dashboard after the Blueprint is applied:
  `RENDER_DEPLOY_HOOK_BACKEND`, `RENDER_DEPLOY_HOOK_FRONTEND`,
  `RENDER_DEPLOY_HOOK_GRAFANA`.

This is the smallest change that fixes driver (a): a deploy becomes an explicit,
observable, CI-gated step, and the hook trigger is build-model-agnostic, so it
applies uniformly to the Docker and static services alike. Implementation is
tracked in **#88** (this spike lands only the decision).

## Alternatives considered
- **Full randomgen pattern (`runtime: image` + registry publish + release-tag
  deploy)** — rejected. Its core driver (avoiding a double build) is moot here,
  it adds registry secrets and a release/tagging workflow sensor_app does not
  have, and the static frontend cannot participate — yielding a split-brain
  deploy model for marginal benefit on a zero-cost demo.
- **Keep `autoDeploy: true`** — rejected. It preserves exactly the reliability
  gap AD-17 documented and keeps deploying on red-CI pushes, with no observable
  deploy step.

## Consequences
- **Deploys are CI-gated and observable.** A push to `main` deploys only after
  its checks pass, and the deploy shows as a job in Actions (green/red) rather
  than an opaque Render webhook. A red pipeline no longer ships.
- **One-time setup** is required before deploys resume: apply the Blueprint,
  create a Deploy Hook per service in Render, and store the three URLs as GitHub
  secrets. Until then the `deploy` steps skip and CI stays green.
- **CodeQL cannot gate the deploy job.** It runs in a separate workflow, and
  cross-workflow `needs:` is not supported; the deploy job gates on the `ci.yml`
  jobs, and branch protection continues to enforce CodeQL as a required check
  before merge to `main`.
- **Every green `main` commit deploys, including docs-only commits.** Accepted
  for a demo; if the redeploy noise (free-tier cold starts) becomes a problem, a
  path filter on the deploy job is a cheap follow-up refinement.
- **The cross-service URL caveat is unchanged** — `CORS_ORIGINS`, `API_URL`,
  `GRAFANA_URL`, and `GF_SERVER_ROOT_URL` must still match the real service URLs
  (see `docs/DEPLOY.md`).
- Refs: randomgen AD-17, #55 (Blueprint), ADR-0004 / ADR-0007 (Render stack),
  epic #12; implementation in #88.
