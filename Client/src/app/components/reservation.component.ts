import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { FlightApiService } from '../services/flight-api.service';
import { Reservation } from '../models/flight.model';

@Component({
  selector: 'app-reservation',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './reservation.component.html',
})
export class ReservationComponent {
  checkNumber = '';
  foundReservation: Reservation | null = null;
  loading = false;
  error = '';

  constructor(
    private flightApi: FlightApiService,
    private cdr: ChangeDetectorRef
  ) {}

  checkReservation(): void {
    this.loading = true;
    this.error = '';
    this.foundReservation = null;
    this.flightApi.getReservation(this.checkNumber.trim().toUpperCase()).subscribe({
      next: res => {
        this.foundReservation = res;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: err => {
        this.error = err.error?.message || 'Nie znaleziono rezerwacji.';
        this.loading = false;
        this.cdr.detectChanges();
      },
    });
  }

  downloadTicket(reservationNumber: string): void {
    window.open(this.flightApi.getTicketPdfUrl(reservationNumber), '_blank');
  }
}