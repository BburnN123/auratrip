import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-itinerary-display',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './itinerary-display.component.html',
  styleUrls: ['./itinerary-display.component.css']
})
export class ItineraryDisplayComponent {
  // This will receive data from Python backend
  @Input() itinerary: any;
}
