import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs/operators';
import { AuthService, Plan } from '../../../services/auth.service';

@Component({
  selector: 'app-altas-manuales',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './altas-manuales.component.html',
  styleUrls: ['./altas-manuales.component.css']
})
export class AltasManualesComponent implements OnInit {
  nuevoUsuario: any = {
    first_name: '',
    last_name: '',
    email: '',
    nif: '',
    sexo: '',
    fecha_nacimiento: '',
    telefono: '',
    id_interno: '',
    cinturon: 'Blanco',
    tipo_plan: null,
    plan_activo: true,
    es_familiar: false
  };

  planes: Plan[] = [];
  guardando: boolean = false;
  mensajeResultado: string | null = null;
  mensajeError: boolean = false;

  opcionesCinturon = [
    'Blanco', 'Azul', 'Morado', 'Marrón', 'Negro',
    'Gris', 'Amarillo', 'Naranja', 'Verde'
  ];

  constructor(private authService: AuthService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.cargarPlanes();
  }

  cargarPlanes() {
    this.authService.getPlanes().subscribe({
      next: (res: Plan[]) => {
        // Solo mostrar planes activos
        this.planes = res.filter(p => p.activo);
      },
      error: (err) => {
        console.error('Error al cargar planes:', err);
      }
    });
  }

  crearAlta() {
    this.guardando = true;
    this.mensajeResultado = null;
    this.mensajeError = false;

    this.authService.crearAltaManual(this.nuevoUsuario)
      .pipe(
        finalize(() => {
          this.guardando = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
      next: (res) => {
        this.mensajeResultado = res.success || 'Usuario creado con éxito. Contraseña: Bjjbfit2026!';
        this.resetearFormulario();
        setTimeout(() => { this.mensajeResultado = null; this.cdr.detectChanges(); }, 5000);
      },
      error: (err) => {
        this.mensajeError = true;
        
        let errorMessage = 'Error al crear el alta manual. Revisa los datos requeridos.';
        if (err.error?.email) {
          errorMessage = 'El email ya está en uso o es inválido.';
        } else if (err.error && typeof err.error === 'object') {
          // Extraer primer error de validación de DRF si existe
          const firstKey = Object.keys(err.error)[0];
          if (firstKey && Array.isArray(err.error[firstKey])) {
            errorMessage = `${firstKey}: ${err.error[firstKey][0]}`;
          }
        }
        
        this.mensajeResultado = errorMessage;
        setTimeout(() => { this.mensajeResultado = null; this.cdr.detectChanges(); }, 8000);
      }
    });
  }

  resetearFormulario() {
    this.nuevoUsuario = {
      first_name: '',
      last_name: '',
      email: '',
      nif: '',
      sexo: '',
      fecha_nacimiento: '',
      telefono: '',
      id_interno: '',
      cinturon: 'Blanco',
      tipo_plan: null,
      plan_activo: true,
      es_familiar: false
    };
  }
}
