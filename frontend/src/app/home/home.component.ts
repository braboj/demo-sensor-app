import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription, catchError, of } from 'rxjs';
import { SensorService } from '../sensors.service';
import { SensorData } from '../sensordata';
import { environment } from '../../environments/environment';

// Cap the live table so an always-open stream cannot grow it without bound.
const MAX_ROWS = 100;

@Component({
  selector: 'app-home',
  imports: [CommonModule],

  /**
   * HomeComponent displays the latest sensor data in a table.
   *
   * Data is loaded once in ngOnInit via the SensorService. The view renders
   * explicit loading, error, and empty states so a failed or empty response
   * never leaves a silent blank table.
   */

  template: `
    <section class="results">
      <h2>Latest Sensor Data</h2>

      @if (grafanaUrl) {
        <p class="grafana-link">
          <a [href]="grafanaUrl" target="_blank" rel="noopener noreferrer">
            View charts in Grafana ↗
          </a>
        </p>
      }

      @if (live) {
        <p class="status status-live" role="status">
          <span aria-hidden="true">●</span> Live — new readings stream in
          automatically.
        </p>
      } @else if (liveError) {
        <p class="status status-error" role="alert">
          Live updates unavailable — showing the latest snapshot. Reload to
          retry.
        </p>
      }

      @if (loading) {
        <p class="status" role="status">Loading sensor data…</p>
      }

      @if (error) {
        <p class="status status-error" role="alert">
          Could not load sensor data. Please try again later.
        </p>
      }

      @if (!loading && !error && sensorDataList.length === 0) {
        <p class="status">No sensor data available yet.</p>
      }

      @if (!loading && !error && sensorDataList.length > 0) {
        <table>
          <caption>
            Latest sensor readings, newest first. Vibration is a coded value: 0
            = none, 1 = detected.
          </caption>

          <thead>
            <tr>
              <th scope="col">Timestamp</th>
              <th scope="col">Temperature</th>
              <th scope="col">Humidity</th>
              <th scope="col">Vibration</th>
            </tr>
          </thead>

          <tbody>
            @for (sensor of sensorDataList; track sensor.id) {
              <tr>
                <td>{{ sensor.timestamp | date: 'medium' }}</td>
                <td>{{ sensor.temperature | number: '1.1-2' }}°C</td>
                <td>{{ sensor.humidity | number: '1.1-2' }}%</td>
                <td>{{ vibrationLabel(sensor.vibration) }}</td>
              </tr>
            }
          </tbody>
        </table>
      }
    </section>
  `,
  styleUrls: ['./home.component.css'],
})
export class HomeComponent implements OnInit, OnDestroy {
  // List of sensor data
  sensorDataList: SensorData[] = [];

  // View state flags
  loading = true;
  error = false;

  // Live-stream state: `live` once events are arriving, `liveError` if the
  // SSE connection failed.
  live = false;
  liveError = false;

  // Optional link to the Grafana dashboard (charting lives there); empty when
  // Grafana is not part of the deploy (see environments/environment*.ts).
  readonly grafanaUrl = environment.grafanaUrl;

  // Inject the sensor service
  private readonly sensorService = inject(SensorService);
  private streamSub?: Subscription;

  // Map the coded vibration value (0/1) to a human-readable label.
  vibrationLabel(value: number): string {
    return value === 1 ? 'Detected' : 'None';
  }

  // Load the initial snapshot once, then start streaming live updates.
  ngOnInit(): void {
    this.sensorService
      .getAllSensorData()
      .pipe(
        catchError(() => {
          this.error = true;
          return of([] as SensorData[]);
        }),
      )
      .subscribe((sensorDataList: SensorData[]) => {
        this.sensorDataList = sensorDataList;
        this.loading = false;
        if (!this.error) {
          this.startLiveUpdates();
        }
      });
  }

  ngOnDestroy(): void {
    this.streamSub?.unsubscribe();
  }

  // Subscribe to the SSE stream and prepend each new reading, newest first.
  private startLiveUpdates(): void {
    this.streamSub = this.sensorService.streamReadings().subscribe({
      next: (reading: SensorData) => {
        this.live = true;
        this.liveError = false;
        // Drop any existing row with the same id (the stream primes with the
        // latest reading, which the initial load may already hold), prepend
        // the new one, and cap the list length.
        const withoutDuplicate = this.sensorDataList.filter(
          (row) => row.id !== reading.id,
        );
        this.sensorDataList = [reading, ...withoutDuplicate].slice(0, MAX_ROWS);
      },
      error: () => {
        this.live = false;
        this.liveError = true;
      },
    });
  }
}
