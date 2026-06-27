import { Component } from '@angular/core';
import { HomeComponent } from './home/home.component';

@Component({
  /**
   * Component storing the content.
   *
   * This is the main component of the application. It contains the header and
   * the main content of the application. The content is handled by the
   * HomeComponent.
   */

  selector: 'app-root',
  imports: [HomeComponent],
  template: `
    <main>
      <!-- Header section is static and contains the logo -->
      <header class="brand-name">
        <img class="brand-logo" src="../assets/logo.svg" alt="" />
      </header>

      <!-- Content section is handled by the home component -->
      <section class="content">
        <app-home></app-home>
      </section>
    </main>
  `,
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  title = 'Sensor Dashboard';
}
