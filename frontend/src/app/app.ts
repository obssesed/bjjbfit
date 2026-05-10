import { Component, signal, OnInit } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  notificacionesPendientes: any[] = [];
  mostrarNotificacionModal = false;
  notificacionActual: any = null;

  constructor(public authService: AuthService, private router: Router) {}

  ngOnInit() {
    if (this.authService.isLoggedIn()) {
      this.authService.cargarPerfil().subscribe();
      this.chequearNotificaciones();
    }
    
    // Escuchar cambios en el login para chequear notificaciones
    this.authService.loggedIn$.subscribe(isLoggedIn => {
      if (isLoggedIn) {
        this.chequearNotificaciones();
      } else {
        this.mostrarNotificacionModal = false;
        this.notificacionesPendientes = [];
      }
    });
  }

  chequearNotificaciones() {
    this.authService.getNotificacionesPendientes().subscribe({
      next: (notifs) => {
        this.notificacionesPendientes = notifs;
        if (this.notificacionesPendientes.length > 0) {
          this.notificacionActual = this.notificacionesPendientes[0];
          this.mostrarNotificacionModal = true;
        }
      },
      error: (err) => console.error('Error al chequear notificaciones', err)
    });
  }

  aceptarNotificacion() {
    if (this.notificacionActual && this.notificacionActual.id) {
      this.authService.marcarNotificacionLeida(this.notificacionActual.id).subscribe({
        next: () => {
          // Quitamos la actual y pasamos a la siguiente si existe
          this.notificacionesPendientes.shift();
          if (this.notificacionesPendientes.length > 0) {
            this.notificacionActual = this.notificacionesPendientes[0];
          } else {
            this.mostrarNotificacionModal = false;
            this.notificacionActual = null;
          }
        },
        error: (err) => {
          console.error('Error al marcar como leída', err);
          this.mostrarNotificacionModal = false;
        }
      });
    }
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
