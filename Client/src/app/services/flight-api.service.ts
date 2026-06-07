import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { AuthService } from './auth.service';
import {
  Flight,
  Reservation,
  FlightSearchParams,
  BookingRequest,
  ApiResponse,
} from '../models/flight.model';

@Injectable({ providedIn: 'root' })
export class FlightApiService {
  private readonly API_URL = window.location.hostname === '192.168.31.62'
    ? 'https://192.168.31.62:8443'
    : 'https://172.23.136.62:8443';

  constructor(
    private http: HttpClient,
    private auth: AuthService
  ) {}

  getFlights(params?: FlightSearchParams): Observable<Flight[]> {
    let httpParams = new HttpParams();
    if (params?.origin)      httpParams = httpParams.set('origin',      params.origin);
    if (params?.destination) httpParams = httpParams.set('destination', params.destination);
    if (params?.date)        httpParams = httpParams.set('date',        params.date);

    return this.http
      .get<ApiResponse<Flight>>(`${this.API_URL}/flights/`, { params: httpParams })
      .pipe(map(res => res.flights ?? []));
  }

  getFlight(id: number): Observable<Flight> {
    return this.http.get<Flight>(`${this.API_URL}/flights/${id}`);
  }

  bookFlight(booking: BookingRequest): Observable<ApiResponse<Reservation>> {
    const headers = this.auth.getAuthHeaders();
    return this.http.post<ApiResponse<Reservation>>(
      `${this.API_URL}/reservations/`,
      booking,
      { headers }
    );
  }

  getMyReservations(): Observable<Reservation[]> {
    const headers = this.auth.getAuthHeaders();
    return this.http
      .get<ApiResponse<Reservation>>(`${this.API_URL}/reservations/`, { headers })
      .pipe(map(res => res.reservations ?? []));
  }

  getReservation(reservationNumber: string): Observable<Reservation> {
    return this.http.get<Reservation>(
      `${this.API_URL}/reservations/${reservationNumber}`
    );
  }

  getTicketPdfUrl(reservationNumber: string): string {
    return `${this.API_URL}/reservations/${reservationNumber}/ticket`;
  }

  cancelReservation(reservationNumber: string): Observable<any> {
    const headers = this.auth.getAuthHeaders();
    return this.http.delete(
      `${this.API_URL}/reservations/${reservationNumber}`,
      { headers }
    );
  }
}