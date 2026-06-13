import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TravelForm } from './travel-form.component';

describe('TravelForm', () => {
  let component: TravelForm;
  let fixture: ComponentFixture<TravelForm>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TravelForm],
    }).compileComponents();

    fixture = TestBed.createComponent(TravelForm);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
