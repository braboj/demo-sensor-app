import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { SensorService } from './sensors.service';
import { SensorData } from './sensordata';
import { environment } from '../environments/environment';

// Minimal stand-in for the browser EventSource so the SSE stream can be
// driven deterministically in tests without a real network connection.
class FakeEventSource {
  static instances: FakeEventSource[] = [];
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  closed = false;

  constructor(public readonly url: string) {
    FakeEventSource.instances.push(this);
  }

  close(): void {
    this.closed = true;
  }

  emit(data: string): void {
    this.onmessage?.(new MessageEvent('message', { data }));
  }

  fail(): void {
    this.onerror?.(new Event('error'));
  }
}

describe('SensorService', () => {
  let service: SensorService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(SensorService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('GETs sensor data from the configured API URL', () => {
    const rows: SensorData[] = [
      {
        id: 1,
        timestamp: '2026-06-27T00:00:00Z',
        temperature: 20,
        humidity: 50,
        vibration: 0,
      },
    ];

    let result: SensorData[] | undefined;
    service.getAllSensorData().subscribe((data) => (result = data));

    const req = httpMock.expectOne(environment.apiUrl);
    expect(req.request.method).toBe('GET');
    req.flush(rows);

    expect(result).toEqual(rows);
  });

  it('propagates an error response to the caller', () => {
    let errored = false;
    service.getAllSensorData().subscribe({
      error: () => (errored = true),
    });

    httpMock.expectOne(environment.apiUrl).flush('fail', {
      status: 500,
      statusText: 'Server Error',
    });

    expect(errored).toBeTrue();
  });

  describe('streamReadings', () => {
    const globalRef = window as unknown as { EventSource: typeof EventSource };
    let originalEventSource: typeof EventSource;

    beforeEach(() => {
      originalEventSource = globalRef.EventSource;
      FakeEventSource.instances = [];
      globalRef.EventSource = FakeEventSource as unknown as typeof EventSource;
    });

    afterEach(() => {
      globalRef.EventSource = originalEventSource;
    });

    it('opens an EventSource at the stream URL and emits parsed readings', () => {
      const received: SensorData[] = [];
      const sub = service
        .streamReadings()
        .subscribe((reading) => received.push(reading));

      const source = FakeEventSource.instances[0];
      expect(source.url).toBe(`${environment.apiUrl}/stream`);

      const row: SensorData = {
        id: 9,
        timestamp: '2026-06-27T00:00:00Z',
        temperature: 20,
        humidity: 50,
        vibration: 0,
      };
      source.emit(JSON.stringify(row));
      expect(received).toEqual([row]);

      sub.unsubscribe();
      expect(source.closed).toBeTrue();
    });

    it('ignores malformed (non-JSON) payloads', () => {
      const received: SensorData[] = [];
      let errored = false;
      const sub = service.streamReadings().subscribe({
        next: (reading) => received.push(reading),
        error: () => (errored = true),
      });

      FakeEventSource.instances[0].emit('not json');

      expect(received).toEqual([]);
      expect(errored).toBeFalse();
      sub.unsubscribe();
    });

    it('errors when the SSE connection fails', () => {
      let errored = false;
      service.streamReadings().subscribe({ error: () => (errored = true) });

      FakeEventSource.instances[0].fail();

      expect(errored).toBeTrue();
    });
  });
});
