import { Component, OnInit, ChangeDetectorRef } from '@angular/core'; // File touched to clear TS cache
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

  activandoId: number | null = null;
  mensajeExito: string | null = null;

  activarPlan(deportista: PerfilDeportista) {
    if (!deportista.tipo_plan_seleccionado) {
      alert("Selecciona un tipo de plan del desplegable primero.");
      return;
    }
    
    this.activandoId = deportista.id;
    this.cdr.detectChanges();

    this.authService.activarPlan(deportista.id, deportista.tipo_plan_seleccionado).subscribe({
      next: () => {
        this.activandoId = null;
        this.mensajeExito = `Plan ${deportista.tipo_plan_seleccionado} activado correctamente para ${deportista.first_name}.`;
        
        // Refrescar toda la carga
        this.cargarUsuarios();
        this.cdr.detectChanges();
        
        setTimeout(() => {
            this.mensajeExito = null;
            this.cdr.detectChanges();
        }, 4000);
      },
      error: (err) => {
        console.error(err);
        this.activandoId = null;
        let errorMessage = "No se pudo activar el plan.";
        if (err.error && err.error.error) {
           errorMessage = err.error.error;
        }
        alert(errorMessage);
        this.cdr.detectChanges();
      }
    });
  }
}
