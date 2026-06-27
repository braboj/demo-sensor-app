import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { catchError, of } from 'rxjs';
import { SensorService } from '../sensors.service';
import { SensorData } from '../sensordata';

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
      <h2>Latest Sensor Data (Hit F5 to refresh, new data every 10 seconds)</h2>

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
export class HomeComponent implements OnInit {
  // List of sensor data
  sensorDataList: SensorData[] = [];

  // View state flags
  loading = true;
  error = false;

  // Inject the sensor service
  private readonly sensorService = inject(SensorService);

  // Map the coded vibration value (0/1) to a human-readable label.
  vibrationLabel(value: number): string {
    return value === 1 ? 'Detected' : 'None';
  }

  // Load data once when the component initializes
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
      });
  }
}
