import { Routes } from '@angular/router';

import { FlightsComponent }      from './components/flights.component';
import { ReservationComponent }  from './components/reservation.component';
import { AuthComponent }         from './components/auth.component';
import { BookComponent }         from './components/book.component';

export const routes: Routes = [
  { path: '',             redirectTo: 'flights', pathMatch: 'full' },
  { path: 'flights',      component: FlightsComponent },
  { path: 'book/:id',     component: BookComponent },
  { path: 'reservations', component: ReservationComponent },
  { path: 'login',        component: AuthComponent },
];