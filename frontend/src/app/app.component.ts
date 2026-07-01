import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  /**
   * Root component: the static header (logo + nav) and a router outlet. Two
   * views are routed — the live readings table (default) and the embedded
   * Grafana charts (see app.routes.ts).
   */

  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <main>
      <!-- Header: primary navigation -->
      <header class="brand-name">
        <nav class="nav" aria-label="Primary">
          <a
            routerLink="/"
            routerLinkActive="active"
            [routerLinkActiveOptions]="{ exact: true }"
            >Live Table</a
          >
          <a routerLink="/charts" routerLinkActive="active">Charts</a>
        </nav>
      </header>

      <!-- Routed view -->
      <section class="content">
        <router-outlet></router-outlet>
      </section>
    </main>
  `,
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  title = 'Sensor Dashboard';
}
