import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ClasesService } from '../../services/clases.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-mi-perfil',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './mi-perfil.component.html',
  styleUrls: ['./mi-perfil.component.css']
})
export class MiPerfilComponent implements OnInit {
  reservasFuturas: any[] = [];
  reservasFinalizadas: any[] = [];
  cargando: boolean = true;
  perfilDeportista: any = null;

  // Modal de cancelación
  showCancelModal: boolean = false;
  reservaSeleccionada: any = null;
  cancelando: boolean = false;
  mensajeResultado: string | null = null;
  mensajeError: boolean = false;

  constructor(private clasesService: ClasesService, private authService: AuthService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.cargarReservas();
    this.cargarPerfil();
  }

  cargarPerfil() {
    this.authService.me().subscribe({
      next: (data) => {
        this.perfilDeportista = data;
        this.cdr.detectChanges();
      },
      error: (err) => console.error('Error cargando perfil', err)
    });
  }

  cargarReservas() {
    this.clasesService.getMisReservas().subscribe({
      next: (data) => {
        const ahora = new Date();
        
        // Separamos logica: Clases pasadas vs Clases futuras
        this.reservasFuturas = [];
        this.reservasFinalizadas = [];

        data.forEach(reserva => {
          if (reserva.estado === 'CANCELADA') return;
          
          const fechaClase = new Date(reserva.clase_detalle.fecha_hora_inicio);
          if (fechaClase.getTime() < ahora.getTime()) {
            this.reservasFinalizadas.push(reserva);
          } else {
            this.reservasFuturas.push(reserva);
          }
        });

        // Ordenar futuras más inminentes primero
        this.reservasFuturas.sort((a, b) => new Date(a.clase_detalle.fecha_hora_inicio).getTime() - new Date(b.clase_detalle.fecha_hora_inicio).getTime());

        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error(err);
        this.cargando = false;
      }
    });
  }

  cancelar(reserva: any) {
    this.reservaSeleccionada = reserva;
    this.showCancelModal = true;
    this.cdr.detectChanges();
  }

  cerrarCancelModal() {
    this.showCancelModal = false;
    this.reservaSeleccionada = null;
    this.cancelando = false;
    this.cdr.detectChanges();
  }

  confirmarCancelacion() {
    if (!this.reservaSeleccionada) return;
    
    this.cancelando = true;
    this.cdr.detectChanges();
    
    const reservaId = this.reservaSeleccionada.id;

    this.clasesService.cancelarReserva(reservaId).subscribe({
      next: () => {
        // Optimistic update: La borramos de la UI
        this.reservasFuturas = this.reservasFuturas.filter(r => r.id !== reservaId);
        this.showCancelModal = false;
        this.reservaSeleccionada = null;
        this.cancelando = false;

        this.mensajeResultado = '✔️ Plaza liberada con éxito.';
        this.mensajeError = false;
        this.cdr.detectChanges();

        setTimeout(() => {
          this.mensajeResultado = null;
          this.cdr.detectChanges();
        }, 4000);
      },
      error: (err) => {
        console.error(err);
        this.cancelando = false;
        this.showCancelModal = false;
        this.reservaSeleccionada = null;

        this.mensajeResultado = '❌ Error al cancelar. Inténtalo de nuevo.';
        this.mensajeError = true;
        this.cdr.detectChanges();
        
        this.cargarReservas(); // Rollback recargando los datos reales

        setTimeout(() => {
          this.mensajeResultado = null;
          this.cdr.detectChanges();
        }, 4000);
      }
    });
  }
}
