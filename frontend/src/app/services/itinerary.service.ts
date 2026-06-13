import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ItineraryService {
  constructor(private http: HttpClient) {}

  getItinerary(): Observable<any> {
    return this.http.get('/api/itinerary'); // Adjust URL to your Python backend
  }
}
