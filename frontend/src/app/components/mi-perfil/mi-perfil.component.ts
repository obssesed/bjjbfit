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
    if(confirm('¿Seguro que deseas cancelar tu clase y devolver tu plaza?')) {
      // Optimistic update: La borramos al instante de la UI
      this.reservasFuturas = this.reservasFuturas.filter(r => r.id !== reserva.id);

      this.clasesService.cancelarReserva(reserva.id).subscribe({
        next: () => {
          console.log("Reserva cancelada en la nube");
        },
        error: (err) => {
          console.error(err);
          alert("Error al cancelar la clase.");
          this.cargarReservas(); // Rollback recargando los datos reales
        }
      });
    }
  }
}
