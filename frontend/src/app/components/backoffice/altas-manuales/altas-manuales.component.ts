import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
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

  constructor(private authService: AuthService) {}

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

    this.authService.crearAltaManual(this.nuevoUsuario).subscribe({
      next: (res) => {
        this.guardando = false;
        this.mensajeResultado = res.success || 'Usuario creado con éxito. Contraseña: Bjjbfit2026!';
        this.resetearFormulario();
        setTimeout(() => { this.mensajeResultado = null; }, 5000);
      },
      error: (err) => {
        this.guardando = false;
        this.mensajeError = true;
        this.mensajeResultado = err.error?.email ? 'El email ya está en uso o es inválido.' : 'Error al crear el alta manual. Revisa los datos requeridos.';
        setTimeout(() => { this.mensajeResultado = null; }, 5000);
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
