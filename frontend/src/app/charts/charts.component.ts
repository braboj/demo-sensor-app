import { Component, inject } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { environment } from '../../environments/environment';

@Component({
  /**
   * ChartsComponent embeds the provisioned Grafana "Sensor Readings" dashboard
   * in an iframe (kiosk mode, which in Grafana 11 hides the outer chrome but
   * keeps the Metric selector and time picker). The URL comes from
   * `environment.grafanaUrl`; when it is empty (Grafana not part of the deploy)
   * the view explains that instead of rendering a broken frame. An "Open in
   * Grafana" link is kept as a full-screen / interactive fallback.
   */
  selector: 'app-charts',
  imports: [],
  template: `
    <section class="charts">
      <h2>Sensor Charts</h2>

      @if (grafanaUrl) {
        <p class="charts-hint">
          Live Grafana dashboard — use the <strong>Metric</strong> selector to
          choose which data points to chart, and see the moving-average trend.
          <a [href]="grafanaUrl" target="_blank" rel="noopener noreferrer">
            Open in Grafana ↗
          </a>
        </p>

        <div class="frame-wrap">
          <iframe
            [src]="embedUrl"
            title="Sensor Readings dashboard (Grafana)"
            loading="lazy"
          ></iframe>
        </div>
      } @else {
        <p class="charts-empty" role="status">
          Charts are not configured for this environment. Set
          <code>GRAFANA_URL</code> at build time to embed the Grafana dashboard,
          or run the full stack with <code>docker compose up</code>.
        </p>
      }
    </section>
  `,
  styleUrls: ['./charts.component.css'],
})
export class ChartsComponent {
  private readonly sanitizer = inject(DomSanitizer);

  // Grafana dashboard URL from the environment (empty disables the embed).
  readonly grafanaUrl = environment.grafanaUrl;

  // `kiosk` drops Grafana's outer nav/sidebar but (Grafana 11) keeps the
  // template-variable selector and time picker; `theme=light` matches the SPA.
  readonly embedUrl: SafeResourceUrl | null = this.grafanaUrl
    ? this.sanitizer.bypassSecurityTrustResourceUrl(
        `${this.grafanaUrl}?kiosk&theme=light`,
      )
    : null;
}
