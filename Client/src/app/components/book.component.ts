import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { FlightApiService } from '../services/flight-api.service';
import { Flight, Reservation, BookingRequest } from '../models/flight.model';

@Component({
  selector: 'app-book',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './book.component.html',
})
export class BookComponent implements OnInit {
  flight: Flight | null = null;
  booking: BookingRequest = { flight_id: 0, passenger_name: '', passenger_email: '', seats: 1 };
  bookingResult: Reservation | null = null;

  loading = false;
  loadingFlight = true;
  error = '';
  success = '';

  constructor(
    private route: ActivatedRoute,
    public router: Router,
    private flightApi: FlightApiService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) { this.router.navigate(['/flights']); return; }

    this.booking.flight_id = +id;
    this.flightApi.getFlight(+id).subscribe({
      next: f => {
        this.flight = f;
        this.loadingFlight = false;
        this.cdr.detectChanges();
      },
      error: err => {
        this.error = 'Nie można załadować lotu.';
        this.loadingFlight = false;
        this.cdr.detectChanges();
      },
    });
  }

  confirm(): void {
    if (!this.booking.passenger_name || !this.booking.passenger_email) {
      this.error = 'Wypełnij wszystkie pola.';
      return;
    }
    this.loading = true;
    this.error = '';
    this.flightApi.bookFlight(this.booking).subscribe({
      next: res => {
        this.bookingResult = res.reservation!;
        this.success = 'Rezerwacja udana!';
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: err => {
        this.error = err.error?.message || 'Błąd rezerwacji.';
        this.loading = false;
        this.cdr.detectChanges();
      },
    });
  }

  downloadTicket(reservationNumber: string): void {
    window.open(this.flightApi.getTicketPdfUrl(reservationNumber), '_blank');
  }

  get totalPrice(): number {
    return this.flight ? this.flight.price * this.booking.seats : 0;
  }
}