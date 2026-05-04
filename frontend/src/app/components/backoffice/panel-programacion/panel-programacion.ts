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
  archivoSeleccionado: File | null = null;
  vistaPreviaImagen: string | null = null;

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

  // Formulario Clase Puntual
  mostrarModalClasePuntual = false;
  mostrarModalError = false;
  mensajeError = '';
  fechaSeleccionadaParaClase: Date | null = null;
  configClasePuntual = {
    plantilla_id: null as number | null,
    hora_inicio: ''
  };

  iconosSugeridos = [];

  constructor(private authService: AuthService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.cargarPlantillas();
    this.cargarCalendario();
  }

  esImagen(icono: string | null | undefined): boolean {
    if (!icono) return false;
    // Si es una URL completa (http) o una ruta relativa de media (/media/)
    return icono.includes('/') || icono.includes('.') || icono.startsWith('http');
  }

  // Helper para asegurar que la imagen tiene la URL del backend si es relativa
  getImagenUrl(url: string | null | undefined): string {
    if (!url) return '';
    if (url.startsWith('http')) return url;
    // Asumimos que si empieza por /media/ es relativa al backend
    return `http://localhost:8000${url}`;
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.archivoSeleccionado = file;
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.vistaPreviaImagen = e.target.result;
        this.cdr.detectChanges();
      };
      reader.readAsDataURL(file);
    }
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
      icono: '',
      hora_inicio: '10:00',
      duracion_minutos: 90,
      capacidad_maxima: 30,
      categoria_acceso: 'ADULTO'
    };
  }

  abrirNueva() {
    this.editando = false;
    this.formPlantilla = this.resetForm();
    this.archivoSeleccionado = null;
    this.vistaPreviaImagen = null;
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

    // Usamos FormData para permitir el envío de archivos
    const formData = new FormData();
    formData.append('titulo', this.formPlantilla.titulo);
    formData.append('icono', this.formPlantilla.icono);
    formData.append('hora_inicio', this.formPlantilla.hora_inicio);
    formData.append('duracion_minutos', this.formPlantilla.duracion_minutos.toString());
    formData.append('capacidad_maxima', this.formPlantilla.capacidad_maxima.toString());
    formData.append('categoria_acceso', this.formPlantilla.categoria_acceso);
    
    if (this.formPlantilla.descripcion) {
      formData.append('descripcion', this.formPlantilla.descripcion);
    }

    if (this.archivoSeleccionado) {
      formData.append('imagen_icono', this.archivoSeleccionado);
    }

    const request = this.editando && this.formPlantilla.id
      ? this.authService.updatePlantilla(this.formPlantilla.id, formData)
      : this.authService.createPlantilla(formData);

    request.subscribe({
      next: () => {
        this.mostrarMensaje(`Programación ${this.editando ? 'actualizada' : 'creada'} correctamente.`);
        this.mostrarModal = false;
        this.archivoSeleccionado = null;
        this.vistaPreviaImagen = null;
        this.cargarPlantillas();
      },
      error: (err) => {
        console.error('Error al guardar:', err);
        alert('Error al guardar la programación.');
      }
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
        this.cargarCalendario();
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

  // --- Lógica del Calendario ---
  fechaCalendario = new Date();
  diasCalendario: { date: Date, classes: any[], isInMonth: boolean }[] = [];
  mesNombres = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

  get mesActualNombre(): string {
    return `${this.mesNombres[this.fechaCalendario.getMonth()]} ${this.fechaCalendario.getFullYear()}`;
  }

  cargarCalendario() {
    const year = this.fechaCalendario.getFullYear();
    const month = this.fechaCalendario.getMonth() + 1;

    this.authService.getClasesPorMes(year, month).subscribe({
      next: (clases) => {
        this.generarDiasCalendario(clases);
        this.cdr.detectChanges();
      },
      error: () => console.error('Error cargando calendario')
    });
  }

  generarDiasCalendario(clases: any[]) {
    this.diasCalendario = [];
    const year = this.fechaCalendario.getFullYear();
    const month = this.fechaCalendario.getMonth();
    
    const primerDiaMes = new Date(year, month, 1);
    const ultimoDiaMes = new Date(year, month + 1, 0);
    
    // Día de la semana en JS: 0=Domingo, 1=Lunes. Lo adaptamos a Lunes=0, Domingo=6.
    let diaInicio = primerDiaMes.getDay() === 0 ? 6 : primerDiaMes.getDay() - 1;

    // Generar días vacíos al principio si el mes no empieza en Lunes
    for (let i = 0; i < diaInicio; i++) {
      this.diasCalendario.push({ date: new Date(year, month, -diaInicio + i + 1), classes: [], isInMonth: false });
    }

    // Generar días del mes
    for (let i = 1; i <= ultimoDiaMes.getDate(); i++) {
      const currentDate = new Date(year, month, i);
      const currentClasses = clases.filter(c => {
        const d = new Date(c.fecha_hora_inicio);
        return d.getDate() === i && d.getMonth() === month && d.getFullYear() === year;
      });
      // Ordenar clases por hora
      currentClasses.sort((a, b) => new Date(a.fecha_hora_inicio).getTime() - new Date(b.fecha_hora_inicio).getTime());
      
      this.diasCalendario.push({ date: currentDate, classes: currentClasses, isInMonth: true });
    }

    // Rellenar hasta completar la última semana
    const celdasRestantes = 42 - this.diasCalendario.length; // 6 semanas max
    for (let i = 1; i <= celdasRestantes; i++) {
      this.diasCalendario.push({ date: new Date(year, month + 1, i), classes: [], isInMonth: false });
    }
  }

  mesAnterior() {
    this.fechaCalendario.setMonth(this.fechaCalendario.getMonth() - 1);
    this.cargarCalendario();
  }

  mesSiguiente() {
    this.fechaCalendario.setMonth(this.fechaCalendario.getMonth() + 1);
    this.cargarCalendario();
  }

  // --- Lógica Interaccional de Calendario ---
  abrirModalClasePuntual(dia: any) {
    if (!dia.isInMonth) return;
    this.fechaSeleccionadaParaClase = dia.date;
    this.configClasePuntual.plantilla_id = null;
    this.configClasePuntual.hora_inicio = '';
    this.mostrarModalClasePuntual = true;
  }

  guardarClasePuntual() {
    if (!this.configClasePuntual.plantilla_id || !this.configClasePuntual.hora_inicio || !this.fechaSeleccionadaParaClase) return;

    const plantilla = this.plantillas.find(p => p.id == this.configClasePuntual.plantilla_id);
    if (!plantilla) return;

    // Construir fechas
    const year = this.fechaSeleccionadaParaClase.getFullYear();
    const month = (this.fechaSeleccionadaParaClase.getMonth() + 1).toString().padStart(2, '0');
    const day = this.fechaSeleccionadaParaClase.getDate().toString().padStart(2, '0');
    const dtInicio = `${year}-${month}-${day}T${this.configClasePuntual.hora_inicio}:00`;
    
    // Asumimos un pequeño cálculo de la fecha_hora_fin añadiendo minutos (en frontend)
    const dtInicioObj = new Date(dtInicio);
    const dtFinObj = new Date(dtInicioObj.getTime() + plantilla.duracion_minutos * 60000);

    const payload = {
      titulo: plantilla.titulo,
      descripcion: plantilla.descripcion || '',
      icono: plantilla.icono,
      categoria_acceso: plantilla.categoria_acceso,
      fecha_hora_inicio: dtInicioObj.toISOString(),
      fecha_hora_fin: dtFinObj.toISOString(),
      capacidad_maxima: plantilla.capacidad_maxima
    };

    this.authService.createClase(payload).subscribe({
      next: () => {
        this.mostrarMensaje('Clase puntual añadida correctamente.');
        this.mostrarModalClasePuntual = false;
        this.cargarCalendario();
      },
      error: (err) => {
        this.mensajeError = err.error?.non_field_errors?.[0] || err.error?.[0] || 'Error al crear la clase puntual.';
        this.mostrarModalError = true;
      }
    });
  }

  mostrarModalEliminarClase = false;
  claseAEliminar: any = null;

  eliminarClase(clase: any, e: Event) {
    e.stopPropagation(); // Evitar que clickee el día (si tuviera evento)
    this.claseAEliminar = clase;
    this.mostrarModalEliminarClase = true;
  }

  confirmarEliminarClase() {
    if (!this.claseAEliminar) return;
    this.authService.deleteClase(this.claseAEliminar.id).subscribe({
      next: () => {
        this.mostrarMensaje('Clase eliminada del calendario.');
        this.mostrarModalEliminarClase = false;
        this.claseAEliminar = null;
        this.cargarCalendario();
      },
      error: () => alert('Error al eliminar la clase.')
    });
  }
}
