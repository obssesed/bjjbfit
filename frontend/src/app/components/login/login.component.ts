import { Component, ChangeDetectorRef } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { take } from 'rxjs/operators';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  username = '';
  password = '';
  errorMsg = '';
  mostrarModalOlvido = false;
  resetUsername = '';
  enviandoSolicitud = false;
  solicitudEnviada = false;

  constructor(
    private authService: AuthService, 
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  login() {
    this.authService.login(this.username, this.password).subscribe({
      next: (perfil) => {
        if (perfil) {
          if (perfil.requiere_cambio_password) {
            this.router.navigate(['/cambio-password']);
          } else {
            this.router.navigate(['/home']);
          }
        } else {
          this.router.navigate(['/home']);
        }
      },
      error: () => {
        this.errorMsg = 'Credenciales incorrectas';
        this.cdr.detectChanges();
      }
    });
  }

  enviarSolicitudReseteo() {
    if (!this.resetUsername) return;
    this.enviandoSolicitud = true;
    this.cdr.detectChanges();
    
    this.authService.solicitarReseteoPassword(this.resetUsername).subscribe({
      next: () => {
        this.enviandoSolicitud = false;
        this.solicitudEnviada = true;
        this.cdr.detectChanges();
      },
      error: () => {
        this.enviandoSolicitud = false;
        this.solicitudEnviada = true;
        this.cdr.detectChanges();
      }
    });
  }

  cerrarModalOlvido() {
    this.mostrarModalOlvido = false;
    this.resetUsername = '';
    this.solicitudEnviada = false;
    this.enviandoSolicitud = false;
    this.cdr.detectChanges();
  }
}
