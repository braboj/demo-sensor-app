# ADR-0008 — Embed the Grafana dashboard in the SPA

**Status:** Accepted (2026-07-01, issue #3 / PR #75)

## Context
Grafana runs as its own service (ADR-0007) and the SPA linked out to it with an
external "View charts in Grafana" link (#67). For the demo, a single page that
shows both the live table and the charts reads as a more integrated product than
sending the reviewer to a separate origin. The question was whether to embed the
dashboard in the Angular app and, if so, how — given the dashboard is served
cross-origin (`sensor-app-grafana.onrender.com`) and browsers block framing by
default (`X-Frame-Options: deny`).

## Decision
Embed the provisioned dashboard in a dedicated **Charts** route rather than only
linking it:

- Angular Router with two views — `/` (Live Table) and `/charts`; the header
  carries the nav.
- `ChartsComponent` renders a **sanitized** `<iframe>` (`DomSanitizer`) of the
  dashboard in **kiosk mode** (`?kiosk&theme=light`) — Grafana 11 kiosk hides
  its own chrome but keeps the metric selector and time picker. An empty
  `grafanaUrl` shows an explanatory empty state instead of a broken frame.
- **Keep the external "Open in Grafana" link** as a full-screen / interactive
  fallback.
- Set **`GF_SECURITY_ALLOW_EMBEDDING=true`** on the Grafana service
  (render.yaml + compose) so the cross-origin SPA can frame it — this drops the
  default `X-Frame-Options: deny`.

## Consequences
- The live demo shows the charts inline; one page tells the whole story.
- **Security posture:** allowing embedding removes clickjacking protection on
  the Grafana origin. Accepted because the instance is **anonymous, read-only**
  (ADR-0007) and exposes only a public sensor dashboard — there is no
  authenticated session or sensitive action to hijack. If Grafana ever gains
  auth or write surfaces, restrict framing to the frontend origin
  (`Content-Security-Policy: frame-ancestors`) instead of blanket embedding.
- The embedded iframe inherits Grafana's free-tier cold start (~30–60s blank on
  first load when idle); the boot splash is visible briefly. A pre-demo warm-up
  (hit the service URLs first) mitigates it; not worth a custom loading overlay.
- Verified locally and live: the built image sends `X-Frame-Options: deny`
  without the flag and omits it with it; on Render, `/charts` embeds the
  dashboard (no `X-Frame-Options`) and the metric selector works inside the
  frame.
