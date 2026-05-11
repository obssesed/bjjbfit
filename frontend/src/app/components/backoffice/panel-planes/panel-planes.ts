import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService, Plan } from '../../../services/auth.service';

@Component({
  selector: 'app-panel-planes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './panel-planes.html',
  styleUrls: ['./panel-planes.css']
})
export class PanelPlanes implements OnInit {
  planes: Plan[] = [];
  cargando = true;
  error: string | null = null;
  mensajeExito: string | null = null;

  // Estado del Modal
  mostrarModal = false;
  editando = false;
  planForm: Plan = {
    nombre: '',
    precio_base: 0,
    beneficios: '',
    categoria_edad: 'ADULTO',
    activo: true
  };

  // Estado del Modal de Confirmación de Borrado
  mostrarConfirmarEliminar = false;
  planAEliminar: Plan | null = null;

  // Modal de Aviso (Sustituye a alert)
  mostrarModalAviso = false;
  tituloAviso = '';
  mensajeAviso = '';
  tipoAviso: 'success' | 'error' | 'warning' = 'warning';

  constructor(
    private authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.cargarPlanes();
  }

  cargarPlanes() {
    this.cargando = true;
    this.authService.getPlanes().subscribe({
      next: (data) => {
        this.planes = data;
        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error cargando planes:', err);
        this.error = 'No se pudieron cargar los planes.';
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  abrirNuevoPlan() {
    this.editando = false;
    this.planForm = {
      nombre: '',
      precio_base: 0,
      beneficios: '',
      categoria_edad: 'ADULTO',
      activo: true
    };
    this.mostrarModal = true;
  }

  editarPlan(plan: Plan) {
    this.editando = true;
    this.planForm = { ...plan };
    this.mostrarModal = true;
  }

  cerrarModal() {
    this.mostrarModal = false;
  }

  guardarPlan() {
    if (!this.planForm.nombre || this.planForm.precio_base < 0) return;

    console.log('Guardando plan...', this.planForm);

    if (this.editando && this.planForm.id) {
      const id = this.planForm.id;
      // Clonamos para no modificar el formulario de la UI
      const datosAEnviar = { ...this.planForm };
      delete datosAEnviar.id; // El ID ya va en la URL, no debe ir en el cuerpo de un PATCH

      this.authService.updatePlan(id, datosAEnviar).subscribe({
        next: () => {
          this.mostrarMensaje('Plan actualizado con éxito.');
          this.cerrarModal();
          this.cargarPlanes();
        },
        error: (err) => {
          console.error('Error guardando plan:', err);
          this.abrirAviso('Error al guardar', 'No se han podido guardar los cambios. Revisa que el nombre no esté duplicado.', 'error');
        }
      });
    } else {
      this.authService.createPlan(this.planForm).subscribe({
        next: () => {
          this.mostrarMensaje('Plan creado con éxito.');
          this.cerrarModal();
          this.cargarPlanes();
        },
        error: (err) => {
          console.error('Error creando plan:', err);
          this.abrirAviso('Error al guardar', 'No se ha podido crear el plan. Revisa los datos.', 'error');
        }
      });
    }
  }

  abrirConfirmarEliminar(plan: Plan) {
    this.planAEliminar = plan;
    this.mostrarConfirmarEliminar = true;
  }

  cerrarConfirmarEliminar() {
    this.mostrarConfirmarEliminar = false;
    this.planAEliminar = null;
  }

  confirmarEliminar() {
    if (!this.planAEliminar || !this.planAEliminar.id) return;

    this.authService.deletePlan(this.planAEliminar.id).subscribe({
      next: () => {
        this.mostrarMensaje('Plan eliminado correctamente.');
        this.cerrarConfirmarEliminar();
        this.cargarPlanes();
      },
      error: (err) => {
        console.error('Error eliminando plan:', err);
        this.abrirAviso('Error de eliminación', 'No se ha podido eliminar el plan seleccionado.', 'error');
        this.cerrarConfirmarEliminar();
      }
    });
  }

  eliminarPlan(id: number | undefined) {
    // Este método queda deprecado en favor de abrirConfirmarEliminar
  }

  private mostrarMensaje(msg: string) {
    this.mensajeExito = msg;
    this.cdr.detectChanges();
    setTimeout(() => {
      this.mensajeExito = null;
      this.cdr.detectChanges();
    }, 4000);
  }

  abrirAviso(titulo: string, mensaje: string, tipo: 'success' | 'error' | 'warning' = 'warning') {
    this.tituloAviso = titulo;
    this.mensajeAviso = mensaje;
    this.tipoAviso = tipo;
    this.mostrarModalAviso = true;
    this.cdr.detectChanges();
  }

  cerrarAviso() {
    this.mostrarModalAviso = false;
    this.cdr.detectChanges();
  }

  getBeneficiosList(beneficios: string): string[] {
    return beneficios.split(/[,\n]/).map(b => b.trim()).filter(b => b.length > 0);
  }
}
