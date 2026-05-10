import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService, PerfilDeportista, Notificacion } from '../../../services/auth.service';

@Component({
  selector: 'app-panel-notificaciones',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './panel-notificaciones.html',
  styleUrl: './panel-notificaciones.css'
})
export class PanelNotificacionesComponent implements OnInit {
  usuarios: PerfilDeportista[] = [];
  nuevaNotificacion: Notificacion = {
    titulo: '',
    mensaje: '',
    es_global: true,
    destinatario: undefined
  };
  
  cargando = false;
  mensajeExito = '';
  mensajeError = '';
  
  notificacionesRecientes: Notificacion[] = [];

  constructor(private authService: AuthService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.cargarUsuarios();
    this.cargarNotificaciones();
  }

  cargarUsuarios() {
    this.authService.getUsuariosActivos().subscribe({
      next: (data) => this.usuarios = data,
      error: (err) => console.error('Error cargando usuarios', err)
    });
  }

  cargarNotificaciones() {
    // Aquí podríamos cargar un historial si el backend lo permite
    // Por ahora el get_queryset del admin devuelve todas
  }

  enviar() {
    if (!this.nuevaNotificacion.titulo || !this.nuevaNotificacion.mensaje) {
      this.mensajeError = 'Título y mensaje son obligatorios.';
      return;
    }

    if (!this.nuevaNotificacion.es_global && !this.nuevaNotificacion.destinatario) {
      this.mensajeError = 'Debes seleccionar un destinatario si no es una notificación global.';
      return;
    }

    this.cargando = true;
    this.mensajeExito = '';
    this.mensajeError = '';

    // Si es global, forzamos destinatario null
    const payload = { ...this.nuevaNotificacion };
    if (payload.es_global) {
        payload.destinatario = undefined;
    }

    console.log('Enviando notificación:', payload);

    this.authService.enviarNotificacion(payload).subscribe({
      next: (res) => {
        this.cargando = false;
        console.log('Respuesta del servidor:', res);
        this.mensajeExito = '¡Notificación enviada correctamente!';
        this.nuevaNotificacion = { titulo: '', mensaje: '', es_global: true, destinatario: undefined };
        this.cdr.detectChanges();
        setTimeout(() => {
          this.mensajeExito = '';
          this.cdr.detectChanges();
        }, 4000);
      },
      error: (err) => {
        console.error('Error al enviar:', err);
        this.cargando = false;
        this.mensajeError = 'Error al enviar la notificación. Revisa la consola.';
      }
    });
  }
}
