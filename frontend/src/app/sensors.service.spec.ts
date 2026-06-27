import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { SensorService } from './sensors.service';
import { SensorData } from './sensordata';
import { environment } from '../environments/environment';

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
});
