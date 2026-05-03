import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, BehaviorSubject, switchMap } from 'rxjs';

export interface Plan {
  id?: number;
  nombre: string;
  precio_base: number;
  beneficios: string;
  categoria_edad: 'ADULTO' | 'JUVENIL' | 'INFANTIL';
  activo: boolean;
}

export interface PlantillaClase {
  id?: number;
  titulo: string;
  descripcion?: string;
  icono: string;
  hora_inicio: string; // "HH:mm:ss"
  duracion_minutos: number;
  capacidad_maxima: number;
  categoria_acceso: 'ADULTO' | 'JUVENIL' | 'INFANTIL';
}

export interface HijoDelegado {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  plan_activo: boolean;
  cinturon: string;
  categoria_plan?: string;
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
  tipo_plan?: number; // Ahora es el ID del objeto Plan
  categoria_plan?: string;
  es_familiar?: boolean;
  tipo_plan_seleccionado?: number; // UI Temporary state
  es_familiar_seleccionado?: boolean; // UI Temporary state
  telefono?: string;
  nif?: string;
  sexo?: string;
  fecha_nacimiento?: string;
  id_interno?: string;
  date_joined?: string;
  hijos_a_cargo: HijoDelegado[];
  is_staff: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private tokenUrl = 'http://127.0.0.1:8000/api/token/';
  private registerUrl = 'http://127.0.0.1:8000/api/deportistas/';
  private meUrl = 'http://127.0.0.1:8000/api/deportistas/me/';
  private apiUrl = 'http://127.0.0.1:8000/api';
  private planesUrl = 'http://127.0.0.1:8000/api/planes/';
  
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

  getUsuariosInactivos(): Observable<PerfilDeportista[]> {
    return this.http.get<PerfilDeportista[]>(`${this.apiUrl}/deportistas/inactivos_backoffice/`);
  }

  getUsuariosPendientes(): Observable<PerfilDeportista[]> {
    return this.http.get<PerfilDeportista[]>(`${this.apiUrl}/deportistas/pendientes_backoffice/`);
  }

  activarPlan(deportistaId: number, planId: number | undefined, esFamiliar: boolean = false): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/deportistas/${deportistaId}/activar_plan/`, { plan_id: planId, es_familiar: esFamiliar });
  }

  darBaja(deportistaId: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/deportistas/${deportistaId}/dar_baja/`, {});
  }

  cambiarPlan(deportistaId: number, planId: number | undefined, esFamiliar: boolean = false): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/deportistas/${deportistaId}/cambiar_plan/`, { plan_id: planId, es_familiar: esFamiliar });
  }

  actualizarGraduacion(deportistaId: number, cinturon: string, grados: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/deportistas/${deportistaId}/actualizar_graduacion/`, { cinturon, grados });
  }

  actualizarIdInterno(deportistaId: number, idInterno: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/deportistas/${deportistaId}/actualizar_id_interno/`, { id_interno: idInterno });
  }


  // --- Gestión de Planes ---
  getPlanes(): Observable<Plan[]> {
    return this.http.get<Plan[]>(this.planesUrl);
  }

  createPlan(plan: Plan): Observable<Plan> {
    return this.http.post<Plan>(this.planesUrl, plan);
  }

  updatePlan(id: number, plan: Plan): Observable<Plan> {
    return this.http.put<Plan>(`${this.planesUrl}${id}/`, plan);
  }

  deletePlan(id: number): Observable<any> {
    return this.http.delete(`${this.planesUrl}${id}/`);
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

  // --- Gestión de Programación (Plantillas) ---
  getPlantillas(): Observable<PlantillaClase[]> {
    return this.http.get<PlantillaClase[]>(`${this.apiUrl}/programacion/`);
  }

  createPlantilla(p: PlantillaClase): Observable<PlantillaClase> {
    return this.http.post<PlantillaClase>(`${this.apiUrl}/programacion/`, p);
  }

  updatePlantilla(id: number, p: PlantillaClase): Observable<PlantillaClase> {
    return this.http.put<PlantillaClase>(`${this.apiUrl}/programacion/${id}/`, p);
  }

  deletePlantilla(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/programacion/${id}/`);
  }

  propagarClases(id: number, config: { fecha_inicio: string, fecha_fin: string, dias_semana: number[] }): Observable<any> {
    return this.http.post(`${this.apiUrl}/programacion/${id}/propagar/`, config);
  }

  // --- Reportes y Métricas ---
  getReporteIngresos(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/deportistas/reporte_ingresos/`);
  }
}
