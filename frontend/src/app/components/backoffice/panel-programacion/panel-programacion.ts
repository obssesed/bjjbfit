import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService, PlantillaClase } from '../../../services/auth.service';

@Component({
  selector: 'app-panel-programacion',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './panel-programacion.html',
  styleUrls: ['./panel-programacion.css']
})
export class PanelProgramacion implements OnInit {
  plantillas: PlantillaClase[] = [];
  cargando = true;
  error: string | null = null;
  mensajeExito: string | null = null;

  // Modales
  mostrarModal = false;
  editando = false;
  mostrarModalPropagar = false;

  // Formulario Plantilla
  formPlantilla: PlantillaClase = this.resetForm();

  // Formulario Propagación
  plantillaSeleccionada: PlantillaClase | null = null;
  configPropagacion = {
    fecha_inicio: '',
    fecha_fin: '',
    dias: [
      { id: 0, nombre: 'Lunes', selected: false },
      { id: 1, nombre: 'Martes', selected: false },
      { id: 2, nombre: 'Miércoles', selected: false },
      { id: 3, nombre: 'Jueves', selected: false },
      { id: 4, nombre: 'Viernes', selected: false },
      { id: 5, nombre: 'Sábado', selected: false },
      { id: 6, nombre: 'Domingo', selected: false }
    ]
  };

  iconosSugeridos = ['🥋', '🤼', '🥊', '🔥', '⏲️', '🏆', '👨‍👩‍👧‍👦', '👶', '🦁'];

  constructor(private authService: AuthService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.cargarPlantillas();
  }

  cargarPlantillas() {
    this.cargando = true;
    this.authService.getPlantillas().subscribe({
      next: (data) => {
        this.plantillas = data;
        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.error = 'Error al cargar programaciones.';
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  resetForm(): PlantillaClase {
    return {
      titulo: '',
      icono: '🥋',
      hora_inicio: '10:00',
      duracion_minutos: 90,
      capacidad_maxima: 30,
      categoria_acceso: 'ADULTO'
    };
  }

  abrirNueva() {
    this.editando = false;
    this.formPlantilla = this.resetForm();
    this.mostrarModal = true;
  }

  editar(p: PlantillaClase) {
    this.editando = true;
    this.formPlantilla = { ...p };
    // Asegurar formato HH:mm para el input time
    if (this.formPlantilla.hora_inicio.length > 5) {
      this.formPlantilla.hora_inicio = this.formPlantilla.hora_inicio.substring(0, 5);
    }
    this.mostrarModal = true;
  }

  guardar() {
    if (!this.formPlantilla.titulo) return;

    const request = this.editando && this.formPlantilla.id
      ? this.authService.updatePlantilla(this.formPlantilla.id, this.formPlantilla)
      : this.authService.createPlantilla(this.formPlantilla);

    request.subscribe({
      next: () => {
        this.mostrarMensaje(`Programación ${this.editando ? 'actualizada' : 'creada'} correctamente.`);
        this.mostrarModal = false;
        this.cargarPlantillas();
      },
      error: (err) => alert('Error al guardar la programación.')
    });
  }

  eliminar(id: number | undefined) {
    if (!id || !confirm('¿Eliminar esta programación? No borrará las clases ya generadas.')) return;
    this.authService.deletePlantilla(id).subscribe({
      next: () => {
        this.mostrarMensaje('Programación eliminada.');
        this.cargarPlantillas();
      }
    });
  }

  // --- Lógica de Propagación ---
  abrirPropagar(p: PlantillaClase) {
    this.plantillaSeleccionada = p;
    this.configPropagacion.fecha_inicio = '';
    this.configPropagacion.fecha_fin = '';
    this.configPropagacion.dias.forEach(d => d.selected = false);
    this.mostrarModalPropagar = true;
  }

  confirmarPropagacion() {
    if (!this.plantillaSeleccionada?.id) return;
    
    const diasSeleccionados = this.configPropagacion.dias
      .filter(d => d.selected)
      .map(d => d.id);

    if (diasSeleccionados.length === 0 || !this.configPropagacion.fecha_inicio || !this.configPropagacion.fecha_fin) {
      alert('Completa fechas y selecciona al menos un día.');
      return;
    }

    this.authService.propagarClases(this.plantillaSeleccionada.id, {
      fecha_inicio: this.configPropagacion.fecha_inicio,
      fecha_fin: this.configPropagacion.fecha_fin,
      dias_semana: diasSeleccionados
    }).subscribe({
      next: (res: any) => {
        this.mostrarMensaje(res.success);
        this.mostrarModalPropagar = false;
      },
      error: (err) => alert('Error al propagar clases. Verifica el rango de fechas.')
    });
  }

  private mostrarMensaje(msg: string) {
    this.mensajeExito = msg;
    this.cdr.detectChanges();
    setTimeout(() => {
      this.mensajeExito = null;
      this.cdr.detectChanges();
    }, 4000);
  }
}
