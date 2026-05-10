import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-cambio-password',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './cambio-password.html',
  styleUrls: ['./cambio-password.css']
})
export class CambioPasswordComponent implements OnInit {
  newPassword = '';
  confirmPassword = '';
  errorMsg = '';
  cargando = false;
  
  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit() {
    // Si no requiere cambio de contraseña, lo sacamos de aquí
    this.authService.userProfile$.subscribe(perfil => {
      if (perfil && !perfil.requiere_cambio_password) {
        this.router.navigate(['/home']);
      }
    });
  }

  cambiarPassword() {
    this.errorMsg = '';
    
    if (this.newPassword.length < 6) {
      this.errorMsg = 'La contraseña debe tener al menos 6 caracteres.';
      return;
    }
    
    if (this.newPassword !== this.confirmPassword) {
      this.errorMsg = 'Las contraseñas no coinciden.';
      return;
    }
    
    this.cargando = true;
    
    this.authService.cambiarPasswordObligatorio(this.newPassword).subscribe({
      next: () => {
        // Recargar el perfil para actualizar el flag a false y poder navegar
        this.authService.cargarPerfil().subscribe({
          next: () => {
            this.router.navigate(['/home']);
          },
          error: () => {
            // Fallback, intentar ir a home
            this.router.navigate(['/home']);
          }
        });
      },
      error: (err) => {
        this.cargando = false;
        this.errorMsg = err.error?.error || 'Error al actualizar la contraseña.';
      }
    });
  }
}
