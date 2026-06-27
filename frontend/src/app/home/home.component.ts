import {Component, OnInit, inject} from '@angular/core';
import {CommonModule} from '@angular/common';
import {catchError, of} from 'rxjs';
import {SensorService} from '../sensors.service';
import {SensorData} from '../sensordata';

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

      <p *ngIf="loading" class="status" role="status">Loading sensor data…</p>

      <p *ngIf="error" class="status status-error" role="alert">
        Could not load sensor data. Please try again later.
      </p>

      <p *ngIf="!loading && !error && sensorDataList.length === 0" class="status">
        No sensor data available yet.
      </p>

      <table *ngIf="!loading && !error && sensorDataList.length > 0">

        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Temperature</th>
            <th>Humidity</th>
            <th>Vibration</th>
          </tr>
        </thead>

        <tbody>
          <tr *ngFor="let sensor of sensorDataList">
            <td>{{ sensor.timestamp }}</td>
            <td>{{ sensor.temperature }}°C</td>
            <td>{{ sensor.humidity }}%</td>
            <td>{{ sensor.vibration }}</td>
          </tr>
        </tbody>
      </table>

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
