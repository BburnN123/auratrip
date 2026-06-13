import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ItineraryDisplay } from './itinerary-display.component';

describe('ItineraryDisplay', () => {
  let component: ItineraryDisplay;
  let fixture: ComponentFixture<ItineraryDisplay>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ItineraryDisplay],
    }).compileComponents();

    fixture = TestBed.createComponent(ItineraryDisplay);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
