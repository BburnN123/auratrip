import { Component, OnInit } from '@angular/core';
import { TravelFormComponent } from './travel-form/travel-form.component';
import { ItineraryDisplayComponent } from './itinerary-display/itinerary-display.component';
import { ItineraryService } from './services/itinerary.service';
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [TravelFormComponent, ItineraryDisplayComponent, HttpClientModule], // 👈 must include here
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'Auratrip1';
  itinerary: any;

  constructor(private itineraryService: ItineraryService) {}

  ngOnInit() {
    this.itineraryService.getItinerary().subscribe(data => {
      this.itinerary = data;
    });
  }
}
