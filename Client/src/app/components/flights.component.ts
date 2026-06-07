import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { FlightApiService } from '../services/flight-api.service';
import { AuthService } from '../services/auth.service';
import { Flight, FlightSearchParams } from '../models/flight.model';

@Component({
  selector: 'app-flights',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './flights.component.html',
})
export class FlightsComponent implements OnInit {
  flights: Flight[] = [];
  loading = false;
  error = '';

  searchParams: FlightSearchParams = {
    origin: '',
    destination: '',
    date: '',
  };

  constructor(
    private flightApi: FlightApiService,
    public auth: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadFlights();
  }

  loadFlights(): void {
    this.loading = true;
    this.error = '';
    this.flightApi.getFlights(this.searchParams).subscribe({
      next: flights => {
        this.flights = flights;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.error = 'Błąd pobierania lotów.';
        this.loading = false;
        this.cdr.detectChanges();
      },
    });
  }

  search(): void { this.loadFlights(); }

  reset(): void {
    this.searchParams = { origin: '', destination: '', date: '' };
    this.loadFlights();
  }

  bookFlight(flight: Flight): void {
    if (!this.auth.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }
    this.router.navigate(['/book', flight.id]);
  }
}