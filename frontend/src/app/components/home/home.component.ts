import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService, PerfilDeportista } from '../../services/auth.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  perfil: PerfilDeportista | null = null;
  activeTab: string = 'nosotros';

  constructor(private authService: AuthService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.authService.me().subscribe({
      next: (usuario) => {
        this.perfil = usuario;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error cargando perfil en Home:', err);
        // Fallback: extraer username del token JWT
        const token = this.authService.getToken();
        if (token) {
          try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            this.perfil = { username: payload.username || payload.user_id || 'Usuario', id: payload.user_id } as any;
          } catch (e) {
            console.error('Error decodificando token:', e);
          }
        }
      }
    });
  }

  setTab(tab: string) {
    this.activeTab = tab;
    // Scroll suave al contenido tras cambiar de tab
    setTimeout(() => {
      const el = document.querySelector('.home-main');
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);
  }

  /** Nombre formateado para el hero */
  get nombreUsuario(): string {
    if (!this.perfil) return 'Deportista';
    return this.perfil.first_name?.trim() || this.perfil.username || 'Deportista';
  }

  /** Cinturón con primera letra en mayúscula */
  get cinturonFormateado(): string {
    if (!this.perfil?.cinturon) return 'Blanco';
    const c = this.perfil.cinturon.toLowerCase();
    return c.charAt(0).toUpperCase() + c.slice(1);
  }

  /** Ampliar vídeo a pantalla completa */
  videoFullscreen(event: Event) {
    const video = (event.target as HTMLElement).closest('.about-video')?.querySelector('video');
    if (video) {
      if (video.requestFullscreen) {
        video.requestFullscreen();
      } else if ((video as any).webkitRequestFullscreen) {
        (video as any).webkitRequestFullscreen();
      }
      video.muted = false;
    }
  }
}
