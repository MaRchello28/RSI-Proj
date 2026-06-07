export interface Flight {
  id: number;
  flight_number: string;
  origin: string;
  destination: string;
  departure_time: string;
  arrival_time: string;
  seats_available: number;
  price: number;
  _links?: HateoasLinks;
}

export interface Reservation {
  id: number;
  reservation_number: string;
  passenger_name: string;
  passenger_email: string;
  seats: number;
  total_price: number;
  created_at: string;
  status: string;
  flight: Flight;
  _links?: HateoasLinks;
}

export interface HateoasLinks {
  [key: string]: { href: string; method: string };
}

export interface FlightSearchParams {
  origin?: string;
  destination?: string;
  date?: string;
}

export interface BookingRequest {
  flight_id: number;
  passenger_name: string;
  passenger_email: string;
  seats: number;
}

export interface ApiResponse<T> {
  message?: string;
  count?: number;
  flights?: T[];
  reservations?: T[];
  reservation?: T;
  _links?: HateoasLinks;
}