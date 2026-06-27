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
): ComponentFixture<HomeComponent> {
  TestBed.configureTestingModule({
    imports: [HomeComponent],
    providers: [{ provide: SensorService, useValue: { getAllSensorData } }],
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
});
