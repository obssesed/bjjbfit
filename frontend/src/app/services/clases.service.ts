import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ClaseBJJ {
  id: number;
  titulo: string;
  descripcion?: string;
  fecha_hora_inicio: string;
  fecha_hora_fin?: string;
  capacidad_maxima: number;
  plazas_disponibles: number;
  plazas_ocupadas: number;
  en_espera: number;
}

@Injectable({
  providedIn: 'root'
})
export class ClasesService {
  private apiUrl = 'http://localhost:8000/api/clases/';
  private reservasUrl = 'http://localhost:8000/api/reservas/';

  constructor(private http: HttpClient) { }

  /**
   * Obtiene la lista de clases disponibles.
   * Usamos headers para evitar que el navegador guarde la respuesta antigua en caché.
   */
  getClases(): Observable<ClaseBJJ[]> {
    // Usamos un query param de tiempo para reventar la caché del navegador.
    // Esto es mucho más seguro porque evita que el sistema de seguridad CORS
    // de Django entre en pánico y bloquee la petición por enviar "Headers Extraños".
    return this.http.get<ClaseBJJ[]>(`${this.apiUrl}?t=${new Date().getTime()}`);
  }

  /**
   * Intenta crear una reserva en Django. 
   * Se enviará automáticamente el JWT del usuario gracias al interceptor.
   */
  hacerReserva(claseId: number, deportistaId?: number): Observable<any> {
    const payload: any = { clase: claseId };
    if (deportistaId) {
      payload.deportista = deportistaId;
    }
    return this.http.post(this.reservasUrl, payload);
  }

  /**
   * Pide a Django las reservas. Como modificamos el Backend, Django ya sabe
   * por el Token JWT quién es el usuario y le devolverá solo las suyas.
   */
  getMisReservas(): Observable<any[]> {
    return this.http.get<any[]>(`${this.reservasUrl}?t=${new Date().getTime()}`);
  }

  /**
   * Ejecuta DELETE sobre la reserva indicada.
   */
  cancelarReserva(reservaId: number): Observable<any> {
    return this.http.delete(`${this.reservasUrl}${reservaId}/`);
  }
}
