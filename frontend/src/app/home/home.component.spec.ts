import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Observable, Subject, of, throwError } from 'rxjs';
import { HomeComponent } from './home.component';
import { SensorService } from '../sensors.service';
import { SensorData } from '../sensordata';

const rows: SensorData[] = [
  {
    id: 1,
    timestamp: '2026-06-27T00:00:00Z',
    temperature: 20,
    humidity: 50,
    vibration: 0,
  },
  {
    id: 2,
    timestamp: '2026-06-27T00:00:10Z',
    temperature: 21,
    humidity: 51,
    vibration: 1,
  },
];

function createFixture(
  getAllSensorData: () => Observable<SensorData[]>,
  streamReadings: () => Observable<SensorData> = () =>
    new Subject<SensorData>(),
): ComponentFixture<HomeComponent> {
  TestBed.configureTestingModule({
    imports: [HomeComponent],
    providers: [
      {
        provide: SensorService,
        useValue: { getAllSensorData, streamReadings },
      },
    ],
  });
  return TestBed.createComponent(HomeComponent);
}

function text(fixture: ComponentFixture<HomeComponent>): string {
  return (fixture.nativeElement as HTMLElement).textContent ?? '';
}

describe('HomeComponent', () => {
  it('should create', () => {
    const fixture = createFixture(() => of(rows));
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('renders one table row per reading on success', () => {
    const fixture = createFixture(() => of(rows));
    fixture.detectChanges(); // runs ngOnInit

    const tableRows = (fixture.nativeElement as HTMLElement).querySelectorAll(
      'tbody tr',
    );
    expect(tableRows.length).toBe(rows.length);
    expect(fixture.componentInstance.loading).toBeFalse();
    expect(fixture.componentInstance.error).toBeFalse();
  });

  it('shows the loading state until data arrives', () => {
    // A subject that never emits keeps the component in its loading state.
    const fixture = createFixture(() => new Subject<SensorData[]>());
    fixture.detectChanges();

    expect(fixture.componentInstance.loading).toBeTrue();
    expect(
      (fixture.nativeElement as HTMLElement).querySelector('[role="status"]'),
    ).toBeTruthy();
    expect(
      (fixture.nativeElement as HTMLElement).querySelector('table'),
    ).toBeNull();
  });

  it('shows the empty state when no readings are returned', () => {
    const fixture = createFixture(() => of([]));
    fixture.detectChanges();

    expect(
      (fixture.nativeElement as HTMLElement).querySelector('table'),
    ).toBeNull();
    expect(text(fixture)).toContain('No sensor data');
  });

  it('shows the error state when the request fails', () => {
    const fixture = createFixture(() => throwError(() => new Error('boom')));
    fixture.detectChanges();

    expect(fixture.componentInstance.error).toBeTrue();
    expect(
      (fixture.nativeElement as HTMLElement).querySelector('[role="alert"]'),
    ).toBeTruthy();
    expect(
      (fixture.nativeElement as HTMLElement).querySelector('table'),
    ).toBeNull();
  });

  it('prepends a streamed reading and shows the live indicator', () => {
    const stream = new Subject<SensorData>();
    const fixture = createFixture(
      () => of(rows),
      () => stream,
    );
    fixture.detectChanges(); // ngOnInit: initial load + subscribe to stream

    const newReading: SensorData = {
      id: 3,
      timestamp: '2026-06-27T00:00:20Z',
      temperature: 22,
      humidity: 52,
      vibration: 0,
    };
    stream.next(newReading);
    fixture.detectChanges();

    expect(fixture.componentInstance.live).toBeTrue();
    expect(fixture.componentInstance.sensorDataList[0].id).toBe(3);
    const tableRows = (fixture.nativeElement as HTMLElement).querySelectorAll(
      'tbody tr',
    );
    expect(tableRows.length).toBe(rows.length + 1);
    expect(text(fixture)).toContain('Live');
  });

  it('replaces rather than duplicates a streamed reading already shown', () => {
    const stream = new Subject<SensorData>();
    const fixture = createFixture(
      () => of(rows),
      () => stream,
    );
    fixture.detectChanges();

    // Re-send an already-shown row (id 2), as the stream's prime event does.
    stream.next({ ...rows[1] });
    fixture.detectChanges();

    const ids = fixture.componentInstance.sensorDataList.map((row) => row.id);
    expect(ids.filter((id) => id === 2).length).toBe(1);
    expect(fixture.componentInstance.sensorDataList.length).toBe(rows.length);
    expect(fixture.componentInstance.sensorDataList[0].id).toBe(2);
  });

  it('shows the live-error state when the stream connection fails', () => {
    const stream = new Subject<SensorData>();
    const fixture = createFixture(
      () => of(rows),
      () => stream,
    );
    fixture.detectChanges();

    stream.error(new Error('SSE connection failed'));
    fixture.detectChanges();

    expect(fixture.componentInstance.live).toBeFalse();
    expect(fixture.componentInstance.liveError).toBeTrue();
    expect(text(fixture)).toContain('Live updates unavailable');
  });

  it('closes the live stream when destroyed', () => {
    const stream = new Subject<SensorData>();
    const fixture = createFixture(
      () => of(rows),
      () => stream,
    );
    fixture.detectChanges();
    expect(stream.observed).toBeTrue();

    fixture.destroy();
    expect(stream.observed).toBeFalse();
  });
});
