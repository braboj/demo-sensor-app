import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';
import { SensorData } from './sensordata';

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

  /**
   * Streams sensor readings live from the backend over Server-Sent Events.
   *
   * Returns a cold Observable that opens an `EventSource` on subscribe and
   * closes it on unsubscribe. Each `data:` message is parsed into a
   * `SensorData`; the Observable errors if the connection fails so callers can
   * render an explicit "live updates unavailable" state instead of silently
   * going stale.
   */
  streamReadings(): Observable<SensorData> {
    return new Observable<SensorData>((subscriber) => {
      const source = new EventSource(`${this.url}/stream`);

      source.onmessage = (event: MessageEvent) => {
        try {
          subscriber.next(JSON.parse(event.data) as SensorData);
        } catch {
          // Ignore malformed payloads; SSE comment heartbeats never reach
          // onmessage, so only a corrupt data frame lands here.
        }
      };

      source.onerror = () =>
        subscriber.error(new Error('SSE connection failed'));

      return () => source.close();
    });
  }
}
