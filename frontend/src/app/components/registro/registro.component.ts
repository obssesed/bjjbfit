import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-registro',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './registro.component.html',
  styleUrls: ['./registro.component.css']
})
export class RegistroComponent {
  registroData = {
    username: '',
    email: '',
    password: '',
    telefono: '',
    cinturon: 'Blanco' // Por defecto para nuevos usuarios
  };
  
  errorMsg: string | null = null;
  cargando: boolean = false;

  constructor(private authService: AuthService, private router: Router) {}

  registrar() {
    this.errorMsg = null;
    
    // Validación básica
    if (!this.registroData.username || !this.registroData.email || !this.registroData.password) {
      this.errorMsg = 'Por favor, rellena los campos obligatorios.';
      return;
    }

    this.cargando = true;

    this.authService.registro(this.registroData).subscribe({
      next: () => {
        // Redirige al login tras registro exitoso
        this.cargando = false;
        alert('Registro exitoso. Ya puedes iniciar sesión.');
        this.router.navigate(['/login']);
      },
      error: (err) => {
        this.cargando = false;
        console.error('Error al registrar usuario', err);
        // Intentar parsear el error de Django si existe
        if (err.error && typeof err.error === 'object') {
          const firstErrorKey = Object.keys(err.error)[0];
          this.errorMsg = `Error (${firstErrorKey}): ${err.error[firstErrorKey][0]}`;
        } else {
          this.errorMsg = 'Ha ocurrido un error durante el registro. Inténtalo de nuevo.';
        }
      }
    });
  }
}
