import { TestBed } from '@angular/core/testing';
import { SensorService } from './sensors.service';
import { SensorData } from './sensordata';

describe('SensorService', () => {
  let service: SensorService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SensorService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('fetches sensor data from the API URL', async () => {
    const rows: SensorData[] = [
      {
        id: 1,
        timestamp: '2026-06-27T00:00:00Z',
        temperature: 20,
        humidity: 50,
        vibration: 0,
      },
    ];
    const fetchSpy = spyOn(window, 'fetch').and.resolveTo(
      new Response(JSON.stringify(rows), { status: 200 }),
    );

    const result = await service.getAllSensorData();

    expect(fetchSpy).toHaveBeenCalledWith(service.url);
    expect(result).toEqual(rows);
  });

  it('returns an empty array when the API responds with null', async () => {
    spyOn(window, 'fetch').and.resolveTo(new Response('null', { status: 200 }));

    const result = await service.getAllSensorData();

    expect(result).toEqual([]);
  });
});
