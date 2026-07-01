import { TestBed } from '@angular/core/testing';
import { ChartsComponent } from './charts.component';

describe('ChartsComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChartsComponent],
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(ChartsComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('embeds an iframe when a Grafana URL is configured', () => {
    const fixture = TestBed.createComponent(ChartsComponent);
    fixture.detectChanges();
    const el = fixture.nativeElement as HTMLElement;
    // The dev/test environment sets grafanaUrl, so the embed should render;
    // if it were empty, the empty-state message renders instead.
    const hasIframe = !!el.querySelector('iframe');
    expect(hasIframe).toBe(!!fixture.componentInstance.grafanaUrl);
  });

  it('offers an external "Open in Grafana" link when configured', () => {
    const fixture = TestBed.createComponent(ChartsComponent);
    fixture.detectChanges();
    const el = fixture.nativeElement as HTMLElement;
    const link = el.querySelector('.charts-hint a');
    if (fixture.componentInstance.grafanaUrl) {
      expect(link?.getAttribute('href')).toBe(
        fixture.componentInstance.grafanaUrl,
      );
    } else {
      expect(link).toBeFalsy();
    }
  });
});
