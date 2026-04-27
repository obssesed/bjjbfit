import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

export interface HijoDelegado {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  plan_activo: boolean;
  cinturon: string;
}

export interface PerfilDeportista {
  id: number;
  username: string;
  email: string;
  cinturon: string;
  grados: number;
  fecha_ultima_graduacion?: string;
  plan_activo: boolean;
  telefono?: string;
  hijos_a_cargo: HijoDelegado[];
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private tokenUrl = 'http://localhost:8000/api/token/';
  private registerUrl = 'http://localhost:8000/api/deportistas/';
  private meUrl = 'http://localhost:8000/api/deportistas/me/';
  
  // Usamos una señal para que el frontend reaccione instantáneamente
  public loggedIn = signal<boolean>(!!localStorage.getItem('access_token'));
  
  constructor(private http: HttpClient) {}

  registro(datos: any): Observable<any> {
    return this.http.post<any>(this.registerUrl, datos);
  }

  login(username: string, password: string): Observable<any> {
    return this.http.post<any>(this.tokenUrl, { username, password })
      .pipe(
        tap(response => {
          if (response && response.access) {
            localStorage.setItem('access_token', response.access);
            this.loggedIn.set(true);
          }
        })
      );
  }

  me(): Observable<PerfilDeportista> {
    return this.http.get<PerfilDeportista>(this.meUrl);
  }

  logout() {
    localStorage.removeItem('access_token');
    this.loggedIn.set(false);
  }

  getToken() {
    return localStorage.getItem('access_token');
  }

  isLoggedIn(): boolean {
    return this.loggedIn();
  }
}
