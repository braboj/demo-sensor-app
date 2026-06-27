import {HttpClient} from '@angular/common/http';
import {Injectable, inject} from '@angular/core';
import {Observable} from 'rxjs';
import {environment} from '../environments/environment';
import {SensorData} from './sensordata';

@Injectable({
  providedIn: 'root',
})
export class SensorService {
  /**
   * Fetches sensor data from the backend API over HttpClient.
   *
   * Errors are intentionally not swallowed here — callers handle them with
   * `catchError` so they can render an explicit error state.
   */

  private readonly http = inject(HttpClient);

  // The sensors endpoint, from the build-time environment config.
  readonly url = environment.apiUrl;

  getAllSensorData(): Observable<SensorData[]> {
    return this.http.get<SensorData[]>(this.url);
  }
}
