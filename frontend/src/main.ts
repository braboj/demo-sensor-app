/*
 *  Protractor support is deprecated in Angular.
 *  Protractor is used in this example for compatibility with Angular documentation tools.
 */
import {
  bootstrapApplication,
  provideProtractorTestingSupport,
} from '@angular/platform-browser';
import { provideZoneChangeDetection } from '@angular/core';
import { provideHttpClient, withFetch } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { AppComponent } from './app/app.component';
import { routes } from './app/app.routes';

bootstrapApplication(AppComponent, {
  providers: [
    // Angular 22 bootstraps zoneless by default; the components still update
    // state via subscribe() + field mutation, so keep zone-driven change
    // detection until they move to signals (the planned OnPush follow-up).
    provideZoneChangeDetection(),
    provideProtractorTestingSupport(),
    provideHttpClient(withFetch()),
    provideRouter(routes),
  ],
}).catch((err) => console.error(err));
