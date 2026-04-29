import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService, PerfilDeportista } from '../../../services/auth.service';

@Component({
  selector: 'app-panel-usuarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './panel-usuarios.html',
  styleUrl: './panel-usuarios.css'
})
export class PanelUsuarios implements OnInit {
  usuariosActivos: PerfilDeportista[] = [];
  usuariosPendientes: PerfilDeportista[] = [];
  usuariosInactivos: PerfilDeportista[] = [];
  cargando: boolean = true;
  error: string | null = null;

  activandoId: number | null = null;
  mensajeExito: string | null = null;

  // Estado de modales y edición
  showBajaModal: boolean = false;
  showCambioPlanModal: boolean = false;
  showGraduacionModal: boolean = false;
  deportistaSeleccionado: PerfilDeportista | null = null;
  editandoIdSocio: number | null = null; // Para edición inline del Nº Socio

  // Filtros
  filtrosExpandidos: boolean = false;
  filtros = {

    texto: '',
    cinturon: '',
    sexo: '',
    categoria: '',
    plan: '',
    fechaAlta: ''
  };

  opcionesCinturon: string[] = ['Blanco', 'Azul', 'Morado', 'Marrón', 'Negro', 'Gris', 'Amarillo', 'Naranja', 'Verde'];

  constructor(

    private authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.cargarUsuarios();
  }

  cargarUsuarios() {
    this.authService.getUsuariosActivos().subscribe({
      next: (dataActivos) => {
        this.usuariosActivos = dataActivos;
        
        // Encadenamos pendientes e inactivos
        this.authService.getUsuariosPendientes().subscribe({
          next: (dataPendientes) => {
            this.usuariosPendientes = dataPendientes;
            
            this.authService.getUsuariosInactivos().subscribe({
              next: (dataInactivos) => {
                this.usuariosInactivos = dataInactivos;
                this.cargando = false;
                this.cdr.detectChanges();
              },
              error: (err) => {
                 this.error = "Error al cargar inactivos.";
                 this.cargando = false;
                 this.cdr.detectChanges();
              }
            });
          },
          error: (err) => {
             this.error = "Error al cargar pendientes.";
             this.cargando = false;
             this.cdr.detectChanges();
          }
        });
      },
      error: (err) => {
        console.error(err);
        this.error = "No se pudieron cargar los datos del Backoffice.";
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  // === Activar Plan (pendientes/inactivos) ===
  activarPlan(deportista: PerfilDeportista) {
    if (!deportista.tipo_plan_seleccionado) {
      // No hay plan seleccionado - mostrar feedback inline
      this.mensajeExito = '⚠️ Selecciona un tipo de plan del desplegable antes de activar.';
      this.cdr.detectChanges();
      setTimeout(() => { this.mensajeExito = null; this.cdr.detectChanges(); }, 4000);
      return;
    }
    
    this.activandoId = deportista.id;
    this.cdr.detectChanges();

    const esFamiliar = deportista.es_familiar_seleccionado || false;

    this.authService.activarPlan(deportista.id, deportista.tipo_plan_seleccionado, esFamiliar).subscribe({
      next: (res) => {
        this.activandoId = null;
        this.mensajeExito = res.success || 'Plan activado correctamente.';
        this.cargarUsuarios();
        this.cdr.detectChanges();
        setTimeout(() => { this.mensajeExito = null; this.cdr.detectChanges(); }, 4000);
      },
      error: (err) => {
        console.error(err);
        this.activandoId = null;
        this.mensajeExito = '❌ ' + (err.error?.error || 'No se pudo activar el plan.');
        this.cdr.detectChanges();
        setTimeout(() => { this.mensajeExito = null; this.cdr.detectChanges(); }, 4000);
      }
    });
  }

  // === Modal Dar de Baja ===
  abrirBaja(deportista: PerfilDeportista) {
    this.deportistaSeleccionado = deportista;
    this.showBajaModal = true;
    this.cdr.detectChanges();
  }

  cerrarBajaModal() {
    this.showBajaModal = false;
    this.deportistaSeleccionado = null;
    this.cdr.detectChanges();
  }

  confirmarBaja() {
    if (!this.deportistaSeleccionado) return;
    
    this.activandoId = this.deportistaSeleccionado.id;
    this.cdr.detectChanges();

    this.authService.darBaja(this.deportistaSeleccionado.id).subscribe({
      next: (res) => {
        this.activandoId = null;
        this.showBajaModal = false;
        this.mensajeExito = res.success || 'Usuario dado de baja.';
        this.deportistaSeleccionado = null;
        this.cargarUsuarios();
        this.cdr.detectChanges();
        setTimeout(() => { this.mensajeExito = null; this.cdr.detectChanges(); }, 4000);
      },
      error: (err) => {
        this.activandoId = null;
        this.showBajaModal = false;
        this.deportistaSeleccionado = null;
        this.mensajeExito = '❌ Error al dar de baja.';
        this.cdr.detectChanges();
        setTimeout(() => { this.mensajeExito = null; this.cdr.detectChanges(); }, 4000);
      }
    });
  }

  // === Modal Cambiar Plan ===
  abrirCambioPlan(deportista: PerfilDeportista) {
    this.deportistaSeleccionado = { ...deportista }; // Clonar para no mutar la lista
    this.deportistaSeleccionado.tipo_plan_seleccionado = '';
    this.deportistaSeleccionado.es_familiar_seleccionado = false;
    this.showCambioPlanModal = true;
    this.cdr.detectChanges();
  }

  cerrarCambioPlanModal() {
    this.showCambioPlanModal = false;
    this.deportistaSeleccionado = null;
    this.cdr.detectChanges();
  }

  confirmarCambioPlan() {
    if (!this.deportistaSeleccionado || !this.deportistaSeleccionado.tipo_plan_seleccionado) return;
    
    this.activandoId = this.deportistaSeleccionado.id;
    this.cdr.detectChanges();

    const esFamiliar = this.deportistaSeleccionado.es_familiar_seleccionado || false;

    this.authService.cambiarPlan(this.deportistaSeleccionado.id, this.deportistaSeleccionado.tipo_plan_seleccionado, esFamiliar).subscribe({
      next: (res) => {
        this.activandoId = null;
        this.showCambioPlanModal = false;
        this.mensajeExito = res.success || 'Plan cambiado.';
        this.deportistaSeleccionado = null;
        this.cargarUsuarios();
        this.cdr.detectChanges();
        setTimeout(() => { this.mensajeExito = null; this.cdr.detectChanges(); }, 4000);
      },
      error: (err) => {
        this.activandoId = null;
        this.showCambioPlanModal = false;
        this.deportistaSeleccionado = null;
        this.mensajeExito = '❌ Error al cambiar plan.';
        this.cdr.detectChanges();
        setTimeout(() => { this.mensajeExito = null; this.cdr.detectChanges(); }, 4000);
      }
    });
  }

  // === Modal Graduación (Cinturón/Grados) ===
  abrirGraduacion(deportista: PerfilDeportista) {
    this.deportistaSeleccionado = { ...deportista }; // Clonar para edición
    this.showGraduacionModal = true;
    this.cdr.detectChanges();
  }

  cerrarGraduacionModal() {
    this.showGraduacionModal = false;
    this.deportistaSeleccionado = null;
    this.cdr.detectChanges();
  }

  cambiarColorCinturon(nuevoColor: string) {
    if (!this.deportistaSeleccionado) return;
    if (this.deportistaSeleccionado.cinturon !== nuevoColor) {
      this.deportistaSeleccionado.cinturon = nuevoColor;
      this.deportistaSeleccionado.grados = 0; // Regla de negocio: reset grados al cambiar cinturón
      this.cdr.detectChanges();
    }
  }

  subirGrado() {
    if (!this.deportistaSeleccionado) return;
    if (this.deportistaSeleccionado.grados < 4) {
      this.deportistaSeleccionado.grados++;
      this.cdr.detectChanges();
    }
  }

  bajarGrado() {
    if (!this.deportistaSeleccionado) return;
    if (this.deportistaSeleccionado.grados > 0) {
      this.deportistaSeleccionado.grados--;
      this.cdr.detectChanges();
    }
  }

  confirmarGraduacion() {
    if (!this.deportistaSeleccionado) return;
    
    this.activandoId = this.deportistaSeleccionado.id;
    this.cdr.detectChanges();

    this.authService.actualizarGraduacion(
      this.deportistaSeleccionado.id, 
      this.deportistaSeleccionado.cinturon, 
      this.deportistaSeleccionado.grados
    ).subscribe({
      next: (res) => {
        this.activandoId = null;
        this.showGraduacionModal = false;
        this.mensajeExito = res.success || 'Graduación actualizada.';
        this.deportistaSeleccionado = null;
        this.cargarUsuarios();
        this.cdr.detectChanges();
        setTimeout(() => { this.mensajeExito = null; this.cdr.detectChanges(); }, 4000);
      },
      error: (err) => {
        this.activandoId = null;
        this.showGraduacionModal = false;
        this.deportistaSeleccionado = null;
        this.mensajeExito = '❌ Error al actualizar graduación.';
        this.cdr.detectChanges();
        setTimeout(() => { this.mensajeExito = null; this.cdr.detectChanges(); }, 4000);
      }
    });
  }

  guardarIdInterno(deportista: PerfilDeportista) {
    if (deportista.id_interno === undefined) return;
    
    this.activandoId = deportista.id;
    this.cdr.detectChanges();

    this.authService.actualizarIdInterno(deportista.id, deportista.id_interno || '').subscribe({
      next: (res) => {
        this.activandoId = null;
        this.editandoIdSocio = null;
        this.mensajeExito = res.success || 'Nº Socio actualizado.';
        this.cdr.detectChanges();
        setTimeout(() => { this.mensajeExito = null; this.cdr.detectChanges(); }, 4000);
      },
      error: (err) => {
        this.activandoId = null;
        this.editandoIdSocio = null;
        this.mensajeExito = '❌ Error al actualizar Nº Socio.';
        this.cdr.detectChanges();
        setTimeout(() => { this.mensajeExito = null; this.cdr.detectChanges(); }, 4000);
      }
    });
  }


  // === Gestión de Filtros (Getters Reactivos) ===
  get usuariosActivosFiltrados(): PerfilDeportista[] {
    return this.aplicarFiltro(this.usuariosActivos);
  }

  get usuariosPendientesFiltrados(): PerfilDeportista[] {
    return this.aplicarFiltro(this.usuariosPendientes);
  }

  get usuariosInactivosFiltrados(): PerfilDeportista[] {
    return this.aplicarFiltro(this.usuariosInactivos);
  }

  private aplicarFiltro(lista: PerfilDeportista[]): PerfilDeportista[] {
    if (!this.filtros) return lista;

    return lista.filter(u => {
      // 1. Texto libre (Nombre, Apellidos, DNI o ID Interno)
      const busqueda = this.filtros.texto.toLowerCase();
      const nombreCompleto = `${u.first_name} ${u.last_name}`.toLowerCase();
      const cumpleTexto = !busqueda || 
        nombreCompleto.includes(busqueda) ||
        (u.id_interno && u.id_interno.toLowerCase().includes(busqueda)) ||
        (u.nif && u.nif.toLowerCase().includes(busqueda));
      
      // 2. Filtros exactos
      const cumpleCinturon = !this.filtros.cinturon || u.cinturon === this.filtros.cinturon;
      const cumpleSexo = !this.filtros.sexo || u.sexo === this.filtros.sexo;
      const cumplePlan = !this.filtros.plan || u.tipo_plan === this.filtros.plan;
      
      // 3. Categoría por edad
      let cumpleCategoria = true;
      if (this.filtros.categoria && u.fecha_nacimiento) {
        const edad = this.calcularEdad(u.fecha_nacimiento);
        if (this.filtros.categoria === 'INFANTIL') cumpleCategoria = edad < 14;
        else if (this.filtros.categoria === 'JUVENIL') cumpleCategoria = edad >= 14 && edad < 18;
        else if (this.filtros.categoria === 'ADULTO') cumpleCategoria = edad >= 18;
      }

      // 4. Fecha de alta (búsqueda por prefijo YYYY-MM-DD)
      let cumpleFecha = true;
      if (this.filtros.fechaAlta && u.date_joined) {
        cumpleFecha = u.date_joined.startsWith(this.filtros.fechaAlta);
      }

      return cumpleTexto && cumpleCinturon && cumpleSexo && cumplePlan && cumpleCategoria && cumpleFecha;
    });
  }

  limpiarFiltros() {
    this.filtros = {
      texto: '',
      cinturon: '',
      sexo: '',
      categoria: '',
      plan: '',
      fechaAlta: ''
    };
    this.cdr.detectChanges();
  }

  // === Exportar Reporte CSV ===
  exportarReporte() {
    // Combinar todos los listados filtrados visibles
    const datos: { deportista: PerfilDeportista; estado: string }[] = [
      ...this.usuariosActivosFiltrados.map(u => ({ deportista: u, estado: 'Activo' })),
      ...this.usuariosPendientesFiltrados.map(u => ({ deportista: u, estado: 'Pendiente' })),
      ...this.usuariosInactivosFiltrados.map(u => ({ deportista: u, estado: 'Inactivo' })),
    ];

    if (datos.length === 0) {
      this.mensajeExito = '⚠️ No hay datos para exportar con los filtros actuales.';
      this.cdr.detectChanges();
      setTimeout(() => { this.mensajeExito = null; this.cdr.detectChanges(); }, 4000);
      return;
    }

    const separador = ';';
    const cabeceras = [
      'Nombre', 'Apellidos', 'DNI/NIF', 'Nº Socio', 'Email', 'Teléfono',
      'Sexo', 'Fecha Nacimiento', 'Categoría', 'Cinturón', 'Grados',
      'Plan', 'Familiar', 'Estado', 'Fecha Alta', 'Hijos a Cargo'
    ];

    const filas = datos.map(({ deportista: u, estado }) => {
      const sexoLabel = u.sexo === 'M' ? 'Masculino' : u.sexo === 'F' ? 'Femenino' : '';
      let categoria = '';
      if (u.fecha_nacimiento) {
        const edad = this.calcularEdad(u.fecha_nacimiento);
        if (edad < 14) categoria = 'Infantil';
        else if (edad < 18) categoria = 'Juvenil';
        else categoria = 'Adulto';
      }
      const planLabel = this.getPlanLabel(u);
      const familiarLabel = u.es_familiar ? 'Sí' : 'No';
      const hijosCount = u.hijos_a_cargo ? u.hijos_a_cargo.length : 0;
      const fechaNac = u.fecha_nacimiento || '';
      const fechaAlta = u.date_joined ? u.date_joined.split('T')[0] : '';

      return [
        u.first_name || '', u.last_name || '', u.nif || '', u.id_interno || '',
        u.email || '', u.telefono || '', sexoLabel, fechaNac, categoria,
        u.cinturon || '', u.grados ?? '', planLabel, familiarLabel,
        estado, fechaAlta, hijosCount
      ].map(val => `"${String(val).replace(/"/g, '""')}"`).join(separador);
    });

    // BOM UTF-8 para que Excel lo lea correctamente con acentos
    const bom = '\uFEFF';
    const contenidoCsv = bom + cabeceras.join(separador) + '\n' + filas.join('\n');

    const blob = new Blob([contenidoCsv], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const enlace = document.createElement('a');
    const hoy = new Date().toISOString().split('T')[0];
    enlace.href = url;
    enlace.download = `reporte_bjjfit_${hoy}.csv`;
    enlace.click();
    window.URL.revokeObjectURL(url);

    this.mensajeExito = `✅ Reporte exportado: ${datos.length} deportista(s).`;
    this.cdr.detectChanges();
    setTimeout(() => { this.mensajeExito = null; this.cdr.detectChanges(); }, 4000);
  }

  // === Helpers ===
  getPlanLabel(u: PerfilDeportista): string {
    if (!u.tipo_plan) return '—';
    const nombres: Record<string, string> = { ADULTO: 'Adulto', JUVENIL: 'Juvenil', INFANTIL: 'Infantil' };
    let label = nombres[u.tipo_plan] || u.tipo_plan;
    if (u.es_familiar) label += ' Fam.';
    return label;
  }

  getPlanesPermitidos(u: PerfilDeportista): { value: string, label: string }[] {
    if (!u.fecha_nacimiento) return [];
    
    const edad = this.calcularEdad(u.fecha_nacimiento);
    
    if (edad < 14) {
      return [{ value: 'INFANTIL', label: 'Mensual Infantil' }];
    } else if (edad < 18) {
      return [{ value: 'JUVENIL', label: 'Mensual Juvenil' }];
    } else {
      return [{ value: 'ADULTO', label: 'Mensual Adulto' }];
    }
  }

  private calcularEdad(fechaStr: string): number {
    const today = new Date();
    const birthDate = new Date(fechaStr);
    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  }
}

