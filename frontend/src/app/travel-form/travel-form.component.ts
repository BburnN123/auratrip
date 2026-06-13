import { Component } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-travel-form',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './travel-form.component.html',
  styleUrls: ['./travel-form.component.css']
})
export class TravelFormComponent {
  travelForm: FormGroup;

  constructor(private fb: FormBuilder) {
    this.travelForm = this.fb.group({
      origin: [''],
      destination: [''],
      startDate: [''],
      endDate: [''],
      mealPreference: ['']
    });
  }

  onSubmit() {
    console.log('Form submitted:', this.travelForm.value);
  }
}
