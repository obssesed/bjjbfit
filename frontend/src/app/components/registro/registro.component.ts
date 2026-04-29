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
    const d = this.registroData;

    // 1. Campos obligatorios
    if (!d.username || !d.email || !d.password || !d.first_name || !d.last_name || !d.nif || !d.sexo || !d.fecha_nacimiento) {
      this.errorMsg = 'Por favor, rellena todos los campos obligatorios marcados con asterisco (*).';
      return;
    }

    // 2. Validar DNI/NIE
    if (!this.validarDNI(d.nif)) {
      this.errorMsg = 'El formato del DNI/NIE no es válido (letra incorrecta o formato erróneo).';
      return;
    }

    // 3. Validar IBAN (si se proporciona)
    if (d.cuenta_bancaria && !this.validarIBAN(d.cuenta_bancaria)) {
      this.errorMsg = 'El número de cuenta bancaria (IBAN) no es válido.';
      return;
    }

    // 4. Validar Teléfono (exactamente 9 dígitos)
    if (!this.validarTelefono(d.telefono)) {
      this.errorMsg = 'El teléfono debe tener exactamente 9 dígitos numéricos.';
      return;
    }

    this.cargando = true;
    this.cdr.detectChanges();


    this.authService.registro(this.registroData).subscribe({
      next: (res) => {
        this.cargando = false;
        this.showExitoModal = true;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.cargando = false;
        console.error('Error detallado de registro:', err);
        this.cdr.detectChanges();
        
        if (err.error && typeof err.error === 'object') {
          const errors = [];
          for (const key in err.error) {
            if (err.error.hasOwnProperty(key)) {
              const msg = Array.isArray(err.error[key]) ? err.error[key][0] : err.error[key];
              errors.push(`${key.toUpperCase()}: ${msg}`);
            }
          }
          this.errorMsg = errors.join(' | ');
        } else if (err.status === 0) {
          this.errorMsg = 'No se pudo conectar con el servidor.';
        } else {
          this.errorMsg = 'Error inesperado al registrar.';
        }
      }
    });
  }

  // === VALIDACIONES AUXILIARES ===

  private validarDNI(dni: string): boolean {
    const nifRegex = /^[0-9]{8}[TRWAGMYFPDXBNJZSQVHLCKE]$/i;
    const nieRegex = /^[XYZ][0-9]{7}[TRWAGMYFPDXBNJZSQVHLCKE]$/i;
    
    dni = dni.toUpperCase().replace(/\s/g, '');

    if (!nifRegex.test(dni) && !nieRegex.test(dni)) return false;

    // Validar letra
    const letras = "TRWAGMYFPDXBNJZSQVHLCKE";
    let numeroStr = dni;
    
    if (nieRegex.test(dni)) {
      // Reemplazar X, Y, Z por 0, 1, 2
      const firstChar = dni.charAt(0);
      const replace = firstChar === 'X' ? '0' : (firstChar === 'Y' ? '1' : '2');
      numeroStr = replace + dni.substring(1);
    }

    const numero = parseInt(numeroStr.substring(0, 8));
    const letraEsperada = letras.charAt(numero % 23);
    
    return dni.charAt(8) === letraEsperada;
  }

  private validarIBAN(iban: string): boolean {
    // Limpiar espacios y guiones
    iban = iban.toUpperCase().replace(/[\s-]/g, '');
    
    // Regex para IBAN español básico (ES + 22 dígitos)
    const ibanRegex = /^ES[0-9]{22}$/;
    if (!ibanRegex.test(iban)) return false;

    // Validación matemática rápida del IBAN (opcionalmente simplificada aquí)
    // Para un MVP robusto, comprobamos que tenga la longitud correcta
    return iban.length === 24;
  }

  private validarTelefono(tel: string): boolean {
    const cleanTel = tel.replace(/\s/g, '');
    return /^[0-9]{9}$/.test(cleanTel);
  }

  private calcularEdad(fecha: string): number {
    const hoy = new Date();
    const cumple = new Date(fecha);
    let edad = hoy.getFullYear() - cumple.getFullYear();
    const m = hoy.getMonth() - cumple.getMonth();
    if (m < 0 || (m === 0 && hoy.getDate() < cumple.getDate())) {
        edad--;
    }
    return edad;
  }



  irALogin() {
    this.showExitoModal = false;
    this.router.navigate(['/login']);
  }

}
