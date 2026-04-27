import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, BehaviorSubject, switchMap } from 'rxjs';

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
  first_name?: string;
  last_name?: string;
  cinturon: string;
  grados: number;
  fecha_ultima_graduacion?: string;
  plan_activo: boolean;
  telefono?: string;
  hijos_a_cargo: HijoDelegado[];
  is_staff: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private tokenUrl = 'http://localhost:8000/api/token/';
  private registerUrl = 'http://localhost:8000/api/deportistas/';
  private meUrl = 'http://localhost:8000/api/deportistas/me/';
  private apiUrl = 'http://localhost:8000/api';
  
  // Usamos BehaviorSubject para asegurar que Angular detecte cambios desde el Nav
  public loggedIn$ = new BehaviorSubject<boolean>(this.checkToken());
  public isStaff$ = new BehaviorSubject<boolean>(false);
  
  constructor(private http: HttpClient) {}

  private checkToken(): boolean {
    if (typeof window !== 'undefined') {
      return !!localStorage.getItem('access_token');
    }
    return false;
  }

  cargarPerfil() {
    return this.me().pipe(
      tap({
        next: (perfil) => this.isStaff$.next(perfil.is_staff),
        error: () => this.isStaff$.next(false)
      })
    );
  }

  registro(datos: any): Observable<any> {
    return this.http.post<any>(this.registerUrl, datos);
  }

  login(username: string, password: string): Observable<any> {
    return this.http.post<any>(this.tokenUrl, { username, password })
      .pipe(
        tap(response => {
          if (response && response.access) {
            localStorage.setItem('access_token', response.access);
            this.loggedIn$.next(true);
          }
        }),
        switchMap(() => this.cargarPerfil())
      );
  }

  me(): Observable<PerfilDeportista> {
    return this.http.get<PerfilDeportista>(this.meUrl);
  }

  logout() {
    localStorage.removeItem('access_token');
    this.loggedIn$.next(false);
    this.isStaff$.next(false);
  }

  getUsuariosActivos(): Observable<PerfilDeportista[]> {
    return this.http.get<PerfilDeportista[]>(`${this.apiUrl}/deportistas/activos_backoffice/`);
  }

  getToken() {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token');
    }
    return null;
  }

  isLoggedIn(): boolean {
    return this.loggedIn$.value;
  }
}
