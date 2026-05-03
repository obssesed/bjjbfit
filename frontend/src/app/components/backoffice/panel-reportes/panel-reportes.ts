import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-panel-reportes',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './panel-reportes.html',
  styleUrls: ['./panel-reportes.css']
})
export class PanelReportesComponent implements OnInit {
  reporte: any = null;
  loading: boolean = true;
  error: string | null = null;

  constructor(private authService: AuthService) {}

  ngOnInit() {
    this.cargarReporte();
  }

  cargarReporte() {
    this.loading = true;
    this.error = null;
    this.authService.getReporteIngresos().subscribe({
      next: (data) => {
        this.reporte = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error al cargar reporte', err);
        this.error = 'No se pudo cargar el reporte económico. Por favor, inténtelo de nuevo.';
        this.loading = false;
      }
    });
  }
}
