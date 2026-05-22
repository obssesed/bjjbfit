import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ClaseBJJ {
  id: number;
  titulo: string;
  descripcion?: string;
  icono: string;
  imagen_icono?: string;
  fecha_hora_inicio: string;
  fecha_hora_fin?: string;
  capacidad_maxima: number;
  plazas_disponibles: number;
  plazas_ocupadas: number;
  en_espera: number;
  categoria_acceso: 'ADULTO' | 'JUVENIL' | 'INFANTIL';
  lista_asistencia?: any[];
}

export interface Actividad {
  id?: number;
  titulo: string;
  descripcion: string;
  badge: string;
  imagen?: string | File;
  orden?: number;
}

export interface Producto {
  id?: number;
  nombre: string;
  descripcion: string;
  tallas: string;
  estado_stock: 'IN_STOCK' | 'LOW_STOCK' | 'OUT_OF_STOCK';
  estado_stock_display?: string;
  imagen?: string | File;
  orden?: number;
}

export interface VideoRepaso {
  id?: number;
  titulo: string;
  descripcion: string;
  fecha_publicacion?: string;
  archivo_video: string | File;
  miniatura?: string | File;
  orden?: number;
}

@Injectable({
  providedIn: 'root'
})
export class ClasesService {
  private apiUrl = `${environment.apiUrl}/clases/`;
  private reservasUrl = `${environment.apiUrl}/reservas/`;
  private actividadesUrl = `${environment.apiUrl}/actividades/`;
  private productosUrl = `${environment.apiUrl}/productos/`;
  private videosUrl = `${environment.apiUrl}/videos-repaso/`;

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

  // --- GESTIÓN DE ACTIVIDADES (Home) ---
  
  getActividades(): Observable<Actividad[]> {
    return this.http.get<Actividad[]>(this.actividadesUrl);
  }

  guardarActividad(actividad: any): Observable<Actividad> {
    const formData = new FormData();
    Object.keys(actividad).forEach(key => {
      if (key === 'imagen' && actividad[key] instanceof File) {
        formData.append(key, actividad[key]);
      } else if (actividad[key] !== null && actividad[key] !== undefined) {
        formData.append(key, actividad[key]);
      }
    });

    if (actividad.id) {
      return this.http.patch<Actividad>(`${this.actividadesUrl}${actividad.id}/`, formData);
    } else {
      return this.http.post<Actividad>(this.actividadesUrl, formData);
    }
  }

  eliminarActividad(id: number): Observable<any> {
    return this.http.delete(`${this.actividadesUrl}${id}/`);
  }

  // --- GESTIÓN DE PRODUCTOS (Tienda) ---

  getProductos(): Observable<Producto[]> {
    return this.http.get<Producto[]>(this.productosUrl);
  }

  guardarProducto(producto: any): Observable<Producto> {
    const formData = new FormData();
    Object.keys(producto).forEach(key => {
      if (key === 'imagen' && producto[key] instanceof File) {
        formData.append(key, producto[key]);
      } else if (producto[key] !== null && producto[key] !== undefined) {
        formData.append(key, producto[key]);
      }
    });

    if (producto.id) {
      return this.http.patch<Producto>(`${this.productosUrl}${producto.id}/`, formData);
    } else {
      return this.http.post<Producto>(this.productosUrl, formData);
    }
  }

  eliminarProducto(id: number): Observable<any> {
    return this.http.delete(`${this.productosUrl}${id}/`);
  }

  // --- GESTIÓN DE VÍDEOS DE REPASO ---

  getVideosRepaso(): Observable<VideoRepaso[]> {
    return this.http.get<VideoRepaso[]>(this.videosUrl);
  }

  guardarVideoRepaso(video: any): Observable<VideoRepaso> {
    const formData = new FormData();
    Object.keys(video).forEach(key => {
      if ((key === 'archivo_video' || key === 'miniatura') && video[key] instanceof File) {
        formData.append(key, video[key]);
      } else if (video[key] !== null && video[key] !== undefined) {
        formData.append(key, video[key]);
      }
    });

    if (video.id) {
      return this.http.patch<VideoRepaso>(`${this.videosUrl}${video.id}/`, formData);
    } else {
      return this.http.post<VideoRepaso>(this.videosUrl, formData);
    }
  }

  eliminarVideoRepaso(id: number): Observable<any> {
    return this.http.delete(`${this.videosUrl}${id}/`);
  }
}
