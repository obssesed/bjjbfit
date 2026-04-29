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

    const request = this.editando && this.planForm.id
      ? this.authService.updatePlan(this.planForm.id, this.planForm)
      : this.authService.createPlan(this.planForm);

    request.subscribe({
      next: () => {
        this.mostrarMensaje(`Plan ${this.editando ? 'actualizado' : 'creado'} con éxito.`);
        this.cerrarModal();
        this.cargarPlanes();
      },
      error: (err) => {
        console.error('Error guardando plan:', err);
        alert('Error al guardar el plan. Revisa los datos.');
      }
    });
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
        alert('No se pudo eliminar el plan.');
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

  getBeneficiosList(beneficios: string): string[] {
    return beneficios.split(/[,\n]/).map(b => b.trim()).filter(b => b.length > 0);
  }
}
