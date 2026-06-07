import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './auth.component.html',
})
export class AuthComponent {
  mode: 'login' | 'register' = 'login';
  username = '';
  password = '';
  loading = false;
  error = '';
  success = '';

  constructor(
    private auth: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  submit(): void {
    this.loading = true;
    this.error = '';
    this.success = '';

    const action = this.mode === 'login'
      ? this.auth.login(this.username, this.password)
      : this.auth.register(this.username, this.password);

    action.subscribe({
      next: () => {
        if (this.mode === 'login') {
          this.router.navigate(['/flights']);
        } else {
          this.success = 'Rejestracja udana! Możesz się zalogować.';
          this.mode = 'login';
        }
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: err => {
        this.error = err.error?.message || 'Wystąpił błąd.';
        this.loading = false;
        this.cdr.detectChanges();
      },
    });
  }

  toggle(): void {
    this.mode = this.mode === 'login' ? 'register' : 'login';
    this.error = '';
    this.success = '';
  }
}