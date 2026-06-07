import { Injectable, signal } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly API_URL = window.location.hostname === '192.168.31.62'
    ? 'https://192.168.31.62:5443'
    : 'https://172.23.136.62:5443';

  isLoggedIn = signal(false);
  currentUsername = signal('');

  constructor(private http: HttpClient) {
    const saved = localStorage.getItem('auth');
    if (saved) {
      const { username } = JSON.parse(saved);
      this.isLoggedIn.set(true);
      this.currentUsername.set(username);
    }
  }

  register(username: string, password: string): Observable<any> {
    return this.http.post(`${this.API_URL}/users/register`, { username, password });
  }

  login(username: string, password: string): Observable<any> {
    const headers = this.buildHeaders(username, password);
    return this.http.get(`${this.API_URL}/users/me`, { headers }).pipe(
      tap(() => {
        localStorage.setItem('auth', JSON.stringify({ username, password }));
        this.isLoggedIn.set(true);
        this.currentUsername.set(username);
      })
    );
  }

  logout(): void {
    localStorage.removeItem('auth');
    this.isLoggedIn.set(false);
    this.currentUsername.set('');
  }

  getAuthHeaders(): HttpHeaders {
    const saved = localStorage.getItem('auth');
    if (!saved) return new HttpHeaders();
    const { username, password } = JSON.parse(saved);
    return this.buildHeaders(username, password);
  }

  private buildHeaders(username: string, password: string): HttpHeaders {
    const encoded = btoa(`${username}:${password}`);
    return new HttpHeaders({ Authorization: `Basic ${encoded}` });
  }
}