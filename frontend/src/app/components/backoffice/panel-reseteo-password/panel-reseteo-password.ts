import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-panel-reseteo-password',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './panel-reseteo-password.html',
  styleUrls: ['./panel-reseteo-password.css']
})
export class PanelReseteoPasswordComponent implements OnInit {
  solicitudes: any[] = [];
  cargando = true;
  modalTempPassword = false;
  tempPasswordData: any = null;

  constructor(private authService: AuthService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.cargarSolicitudes();
  }

  cargarSolicitudes() {
    this.cargando = true;
    this.authService.getSolicitudesReseteoPendientes().subscribe({
      next: (res) => {
        this.solicitudes = res;
        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  aprobarSolicitud(id: number) {
    this.authService.aprobarSolicitudReseteo(id).subscribe({
      next: (res) => {
        // res contiene temp_password y username
        this.tempPasswordData = res;
        this.modalTempPassword = true;
        this.cargarSolicitudes(); // Recargar la lista
        this.cdr.detectChanges();
      },
      error: (err) => {
        alert(err.error?.error || 'Error al aprobar solicitud.');
      }
    });
  }

  cerrarModal() {
    this.modalTempPassword = false;
    this.tempPasswordData = null;
  }
}
