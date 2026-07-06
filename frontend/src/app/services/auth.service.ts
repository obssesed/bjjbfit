import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, BehaviorSubject, switchMap } from 'rxjs';
import { environment } from '../../environments/environment';

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
  imagen_icono?: string;
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
  id_interno?: string;
}

export interface Notificacion {
  id?: number;
  titulo: string;
  mensaje: string;
  fecha_creacion?: string;
  es_global: boolean;
  destinatario?: number;
  leida?: boolean;
}

/** Interfaz para el perfil completo del deportista */
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
  tipo_plan?: number;
  categoria_plan?: string;
  es_familiar?: boolean;
  requiere_cambio_password?: boolean;
  tipo_plan_seleccionado?: number;
  es_familiar_seleccionado?: boolean;
  telefono?: string;
  nif?: string;
  sexo?: string;
  fecha_nacimiento?: string;
  id_interno?: string;
  cuenta_bancaria?: string;
  metodo_pago?: 'EFECTIVO' | 'CUENTA';
  date_joined?: string;
  is_staff: boolean;
  hijos_a_cargo: HijoDelegado[];
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private tokenUrl = `${environment.apiUrl}/token/`;
  private registerUrl = `${environment.apiUrl}/deportistas/`;
  private meUrl = `${environment.apiUrl}/deportistas/me/`;
  private planesUrl = `${environment.apiUrl}/planes/`;

  public loggedIn$ = new BehaviorSubject<boolean>(this.checkToken());
  public isStaff$ = new BehaviorSubject<boolean>(this.getCachedStaff());
  private userProfileSubject = new BehaviorSubject<PerfilDeportista | null>(this.getCachedProfile());
  public userProfile$ = this.userProfileSubject.asObservable();

  constructor(private http: HttpClient) { }

  private checkToken(): boolean {
    if (typeof window !== 'undefined') {
      return !!localStorage.getItem('access_token');
    }
    return false;
  }

  cargarPerfil() {
    return this.me().pipe(
      tap({
        next: (perfil) => {
          this.isStaff$.next(perfil.is_staff);
          this.userProfileSubject.next(perfil);
          if (typeof window !== 'undefined') {
            localStorage.setItem('user_profile', JSON.stringify(perfil));
          }
        },
        error: () => this.logout()
      })
    );
  }

  private getCachedProfile(): PerfilDeportista | null {
    if (typeof window !== 'undefined') {
      const cached = localStorage.getItem('user_profile');
      if (cached) {
        try {
          return JSON.parse(cached);
        } catch (e) {
          return null;
        }
      }
    }
    return null;
  }

  private getCachedStaff(): boolean {
    const profile = this.getCachedProfile();
    return profile ? profile.is_staff : false;
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

  actualizarPerfil(datos: any): Observable<PerfilDeportista> {
    return this.http.patch<PerfilDeportista>(this.meUrl, datos);
  }

  actualizarPerfilHijo(hijoId: number, datos: any): Observable<PerfilDeportista> {
    return this.http.patch<PerfilDeportista>(`${this.apiUrl}/deportistas/${hijoId}/actualizar_perfil_hijo/`, datos);
  }

  anadirHijo(datos: any): Observable<PerfilDeportista> {
    return this.http.post<PerfilDeportista>(`${this.apiUrl}/deportistas/crear_perfil_hijo/`, datos);
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_profile');
    this.loggedIn$.next(false);
    this.isStaff$.next(false);
    this.userProfileSubject.next(null);
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

  actualizarNif(deportistaId: number, nif: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/deportistas/${deportistaId}/actualizar_nif/`, { nif });
  }

  actualizarNombre(deportistaId: number, firstName: string, lastName: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/deportistas/${deportistaId}/actualizar_nombre/`, { first_name: firstName, last_name: lastName });
  }

  crearAltaManual(datos: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/deportistas/crear_alta_manual/`, datos);
  }

  actualizarDatosPago(deportistaId: number, metodoPago: string, cuentaBancaria: string): Observable<any> {
    return this.http.patch<any>(`${this.apiUrl}/deportistas/${deportistaId}/`, {
      metodo_pago: metodoPago,
      cuenta_bancaria: cuentaBancaria
    });
  }

  getPlanes(): Observable<Plan[]> {
    return this.http.get<Plan[]>(this.planesUrl);
  }

  createPlan(plan: Plan): Observable<Plan> {
    return this.http.post<Plan>(this.planesUrl, plan);
  }

  updatePlan(id: number, plan: any): Observable<Plan> {
    // Usamos patch para evitar errores de unicidad si el nombre no cambia
    return this.http.patch<Plan>(`${this.planesUrl}${id}/`, plan);
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

  getPlantillas(): Observable<PlantillaClase[]> {
    return this.http.get<PlantillaClase[]>(`${this.apiUrl}/programacion/`);
  }

  createPlantilla(p: any): Observable<PlantillaClase> {
    return this.http.post<PlantillaClase>(`${this.apiUrl}/programacion/`, p);
  }

  updatePlantilla(id: number, p: any): Observable<PlantillaClase> {
    // Usamos patch para permitir subir archivos sin tener que mandar todo el objeto de nuevo obligatoriamente
    return this.http.patch<PlantillaClase>(`${this.apiUrl}/programacion/${id}/`, p);
  }

  deletePlantilla(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/programacion/${id}/`);
  }

  propagarClases(id: number, config: { fecha_inicio: string, fecha_fin: string, dias_semana: number[] }): Observable<any> {
    return this.http.post(`${this.apiUrl}/programacion/${id}/propagar/`, config);
  }

  getClasesPorMes(year: number, month: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/clases/?year=${year}&month=${month}`);
  }

  createClase(clase: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/clases/`, clase);
  }

  deleteClase(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/clases/${id}/`);
  }

  getReporteIngresos(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/deportistas/reporte_ingresos/`);
  }

  getReporteAnual(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/deportistas/reporte_anual/`);
  }

  getNotificacionesPendientes(): Observable<Notificacion[]> {
    return this.http.get<Notificacion[]>(`${this.apiUrl}/notificaciones/pendientes/`);
  }

  marcarNotificacionLeida(id: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/notificaciones/${id}/leer/`, {});
  }

  enviarNotificacion(notif: Notificacion): Observable<Notificacion> {
    return this.http.post<Notificacion>(`${this.apiUrl}/notificaciones/`, notif);
  }

  // --- Recuperación de Contraseña ---
  solicitarReseteoPassword(username: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/deportistas/solicitar_reseteo/`, { username });
  }

  getSolicitudesReseteoPendientes(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/solicitudes-reseteo/`);
  }

  aprobarSolicitudReseteo(id: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/solicitudes-reseteo/${id}/aprobar/`, {});
  }

  cambiarPasswordObligatorio(new_password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/deportistas/cambiar_password_obligatorio/`, { new_password });
  }
}
