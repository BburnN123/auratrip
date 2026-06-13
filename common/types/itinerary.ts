export interface Itinerary {
  id: string;
  tripId: string;
  days: Array<Record<string, unknown>>;
}
