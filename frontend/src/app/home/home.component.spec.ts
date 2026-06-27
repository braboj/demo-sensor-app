import { ComponentFixture, TestBed } from '@angular/core/testing';
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

describe('HomeComponent', () => {
  let fixture: ComponentFixture<HomeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HomeComponent],
      providers: [
        {
          provide: SensorService,
          useValue: { getAllSensorData: () => Promise.resolve(rows) },
        },
      ],
    }).compileComponents();
    fixture = TestBed.createComponent(HomeComponent);
  });

  it('should create', () => {
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('loads sensor data from the service', async () => {
    await fixture.whenStable();
    expect(fixture.componentInstance.sensorDataList).toEqual(rows);
  });

  it('renders one table row per reading', async () => {
    await fixture.whenStable();
    fixture.detectChanges();
    const tableRows = (fixture.nativeElement as HTMLElement).querySelectorAll(
      'tbody tr',
    );
    expect(tableRows.length).toBe(rows.length);
  });
});
