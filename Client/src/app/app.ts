import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <nav class="navbar">
      <span class="brand">✈ FlightApp</span>
      <div class="nav-links">
        <a routerLink="/flights" routerLinkActive="active">Loty</a>
        <a routerLink="/reservations" routerLinkActive="active">Sprawdź rezerwację</a>
        <ng-container *ngIf="auth.isLoggedIn(); else loginLink">
          <span class="username">{{ auth.currentUsername() }}</span>
          <a (click)="logout()" class="logout">Wyloguj</a>
        </ng-container>
        <ng-template #loginLink>
          <a routerLink="/login" routerLinkActive="active">Zaloguj</a>
        </ng-template>
      </div>
    </nav>
    <main>
      <router-outlet />
    </main>
  `,
  styles: [`
    .navbar {
      background: #1a3a5c;
      color: white;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.8rem 2rem;
    }
    .brand { font-size: 1.3rem; font-weight: 700; letter-spacing: 1px; }
    .nav-links { display: flex; gap: 1.2rem; align-items: center; }
    .nav-links a { color: #a8c8e8; text-decoration: none; cursor: pointer; }
    .nav-links a.active, .nav-links a:hover { color: white; }
    .username { color: #ffd700; font-weight: 600; }
    .logout { color: #ff8080 !important; cursor: pointer; }
    main { max-width: 960px; margin: 0 auto; padding: 1rem; }
  `]
})
export class App {
  constructor(public auth: AuthService, private router: Router) {}

  logout(): void {
    this.auth.logout();
    this.router.navigate(['/flights']);
  }
}