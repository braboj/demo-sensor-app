import { Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { ChartsComponent } from './charts/charts.component';

// Two views: the live readings table (default) and the embedded Grafana charts.
export const routes: Routes = [
  { path: '', component: HomeComponent, pathMatch: 'full' },
  { path: 'charts', component: ChartsComponent },
  { path: '**', redirectTo: '' },
];
