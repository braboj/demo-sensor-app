# ADR-0010 — Scale multi-service Render deploys with a manifest-driven CI matrix

**Status:** Accepted (2026-07-02, spike #91) — target design; generalizes ADR-0009

## Context
ADR-0009 made deploys CI-triggered by POSTing one hardcoded Render deploy hook
per service, each hook stored as its own GitHub secret. That is deliberately the
**small-fleet mechanism** (≤ ~5 services; implemented in #88).

This ADR takes the design exercise of treating sensor_app as the
**many-services extreme** and asks: what deploy design **stays on Render** but
scales to that shape? At scale the ADR-0009 mechanism breaks on every axis:

- **Secrets.** One `RENDER_DEPLOY_HOOK_<SVC>` per service hits GitHub's ~100
  repo-secret cap and becomes a manual rotation burden.
- **Workflow churn.** A hardcoded `trigger <svc>` step per service means editing
  `ci.yml` for every new service.
- **Blast radius.** Every green push to `main` POSTs *all* hooks, so a one-line
  change redeploys the whole fleet (and stampedes Render's build concurrency).
- **No control plane.** Fire-and-forget hooks give no deploy status, no
  ordering/dependencies, no health gating, and no rollback.

The chosen platform is **Render, pushed to its limit**. Render scales cleanly to
roughly *tens* of services; it is **not** a hundreds-of-services platform (no
native GitOps/reconciliation, account-level build-concurrency limits, shared
free instance hours). That ceiling is recorded under Consequences as the
explicit revisit threshold.

## Decision
Replace per-service hooks with a **data-driven, manifest-first** deploy that
Render's REST API drives from CI:

1. **Service manifest** — a version-controlled `deploy/services.json`, the single
   source of truth for what deploys, from which changes, and in what order:

   ```json
   [
     { "name": "backend",  "serviceId": "srv-…", "tier": 0, "paths": ["backend/**"] },
     { "name": "frontend", "serviceId": "srv-…", "tier": 1, "paths": ["frontend/**"] },
     { "name": "grafana",  "serviceId": "srv-…", "tier": 1, "paths": ["deploy/grafana/**"] }
   ]
   ```

2. **One credential** — a single `RENDER_API_KEY` secret, not N hook URLs.
   Deploy via `POST /v1/services/{serviceId}/deploys`, which returns a deploy id
   to poll. This removes the secret-cap and rotation problems in one move.

3. **Change detection** — a CI `plan` job diffs the push against each manifest
   entry's `paths` and emits the JSON list of services to deploy. A docs-only or
   unrelated change yields an empty list, so nothing redeploys.

4. **Dynamic matrix** — a `deploy` job consumes that list as
   `strategy.matrix.service = fromJSON(needs.plan.outputs.services)`: one leg per
   changed service, per-service status in the Actions UI, and **no workflow edit
   when a service is added** — only a manifest row.

5. **Ordering by tier** — the manifest's `tier` sequences waves: tier 0 (backend,
   which runs migrations) must go healthy before tier 1 (frontend + grafana)
   starts. Implemented as tier-ordered jobs joined by `needs`.

6. **Status + rollback** — each leg polls the Render API for the deploy result
   and health check and fails the job on a failed deploy; because Render retains
   prior deploys, a failed leg can trigger an API rollback to the last-good
   deploy (documented, optionally automated).

### Reference topology

```
push to main
    │
    ▼
[ plan ]  reads deploy/services.json, diffs changed paths vs each entry
    │        → outputs services = ["backend"]   (JSON, may be empty)
    ▼
[ deploy ]  strategy.matrix.service = fromJSON(needs.plan.outputs.services)
    │        one RENDER_API_KEY for all legs — no per-service secrets
    │
    ├─ tier 0 ─ backend ─ POST /v1/services/$ID/deploys ─ poll ─ /health
    │              (runs migrations)                          │
    │                                              fail ⇒ API rollback to last good
    ▼  (tier 0 healthy)
    ├─ tier 1 ─ frontend ─ POST …/deploys ─ poll ─ health
    └─ tier 1 ─ grafana  ─ POST …/deploys ─ poll ─ health
```

## Alternatives considered
- **Keep ADR-0009's per-service hooks** — rejected at scale: N secrets (cap +
  rotation), per-service workflow edits, deploy-everything blast radius, no
  status/ordering/rollback. It remains correct *below* this design's scale.
- **GitOps / Kubernetes (Argo CD or Flux)** — the true hundreds-of-services
  answer (declarative reconciliation, ordered progressive/canary rollout,
  self-healing, immutable digests). Rejected *here* because it means leaving
  Render and vastly exceeds a demo's needs; it is the **next tier** once Render's
  ceiling is hit, not this one.
- **Render Blueprint `autoDeploy` only** — rejected for ADR-0009's reasons
  (unreliable, not CI-gated).

## Consequences
- **Adding a service is one manifest row** (name, id, tier, paths) — no `ci.yml`
  edit and no new secret. This is the property that makes it scale to tens of
  services.
- **One credential** to rotate instead of N; smaller secret surface.
- **Only changed services deploy**, so docs-only commits cause no redeploy storm
  and Render's build concurrency is not stampeded.
- **A real control plane**: per-service deploy status, tier-ordered rollout,
  health-gated deploys, and rollback via the Render API.
- **Render ceiling / revisit threshold.** Beyond ~tens of services — or when
  cross-environment promotion, canary/progressive rollout, or declarative
  reconciliation are needed — migrate to the GitOps/K8s tier with immutable
  digests. Notably the ADR-0009 rationale for skipping `runtime: image` (no
  CI-built image to reuse) **inverts** at that tier: build-once-promote-a-digest
  becomes mandatory. See the sibling `demo-randomgen` AD-17 (the `runtime: image`
  + hook pattern) and the general principle upstreamed as
  solid-ai-templates#717.
- **Relationship to ADR-0009 / #88 / #90.** This generalizes ADR-0009: the
  hook-per-service is the degenerate one-tier, no-change-detection instance of
  the same "CI-triggered, not push-based" principle. Implementing this design
  would supersede the hardcoded hooks (#88 / PR #90); until then, #90 stays the
  current small-fleet mechanism and this ADR is the documented target.
- **This is a design ADR** — no `deploy/services.json`, `RENDER_API_KEY`, or
  `ci.yml` matrix ships in this change; implementation is a separate ticket to be
  opened when the fleet actually grows toward this design.
