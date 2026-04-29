import { Component, ChangeDetectorRef } from '@angular/core';
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
    first_name: '',
    last_name: '',
    nif: '',
    sexo: '',
    fecha_nacimiento: '',
    telefono: '',
    cuenta_bancaria: '',
    cinturon: 'Blanco'
  };
  
  errorMsg: string | null = null;
  cargando: boolean = false;
  showExitoModal: boolean = false;

  constructor(
    private authService: AuthService, 
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  registrar() {
    this.errorMsg = null;
    console.log('Iniciando proceso de registro...', this.registroData);
    
    // Validación básica obligatoria según negocio
    const d = this.registroData;
    if (!d.username || !d.email || !d.password || !d.first_name || !d.last_name || !d.nif || !d.sexo || !d.fecha_nacimiento) {
      this.errorMsg = 'Por favor, rellena todos los campos obligatorios marcados con asterisco (*).';
      return;
    }

    this.cargando = true;
    this.cdr.detectChanges();

    this.authService.registro(this.registroData).subscribe({
      next: (res) => {
        console.log('Registro exitoso en el servidor!', res);
        this.cargando = false;
        this.showExitoModal = true;
        this.cdr.detectChanges(); // Forzamos a Angular a mostrar el modal
      },
      error: (err) => {
        this.cargando = false;
        console.error('Error detallado de registro:', err);
        this.cdr.detectChanges();
        
        if (err.error && typeof err.error === 'object') {
          // Extraer mensajes de error de Django REST Framework
          const errors = [];
          for (const key in err.error) {
            if (err.error.hasOwnProperty(key)) {
              const msg = Array.isArray(err.error[key]) ? err.error[key][0] : err.error[key];
              errors.push(`${key.toUpperCase()}: ${msg}`);
            }
          }
          this.errorMsg = errors.join(' | ');
        } else if (err.status === 0) {
          this.errorMsg = 'No se pudo conectar con el servidor. Revisa tu conexión.';
        } else {
          this.errorMsg = 'Error inesperado. Por favor, revisa los datos e inténtalo de nuevo.';
        }
      }
    });
  }


  irALogin() {
    this.showExitoModal = false;
    this.router.navigate(['/login']);
  }

}
