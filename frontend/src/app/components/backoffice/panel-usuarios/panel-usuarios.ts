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

  // Estado de modales
  showBajaModal: boolean = false;
  showCambioPlanModal: boolean = false;
  deportistaSeleccionado: PerfilDeportista | null = null;

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

  // === Helpers ===
  getPlanLabel(u: PerfilDeportista): string {
    if (!u.tipo_plan) return '—';
    const nombres: Record<string, string> = { ADULTO: 'Adulto', JUVENIL: 'Juvenil', INFANTIL: 'Infantil' };
    let label = nombres[u.tipo_plan] || u.tipo_plan;
    if (u.es_familiar) label += ' Fam.';
    return label;
  }
}
