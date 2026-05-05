import { Component, OnInit } from '@angular/core';
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

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.authService.me().subscribe(usuario => {
      this.perfil = usuario;
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
    if (!this.perfil) return '';
    return this.perfil.first_name || this.perfil.username;
  }

  /** Cinturón con primera letra en mayúscula */
  get cinturonFormateado(): string {
    if (!this.perfil?.cinturon) return 'Blanco';
    const c = this.perfil.cinturon.toLowerCase();
    return c.charAt(0).toUpperCase() + c.slice(1);
  }
}
