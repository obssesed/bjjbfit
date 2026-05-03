import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
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
  mesSeleccionado: string = 'mes_actual';

  constructor(private authService: AuthService, private cdr: ChangeDetectorRef) {}

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
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al cargar reporte', err);
        this.error = 'No se pudo cargar el reporte económico. Por favor, inténtelo de nuevo.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  seleccionarMes(mesKey: string) {
    this.mesSeleccionado = mesKey;
    this.cdr.detectChanges();
  }

  exportarCSV() {
    if (!this.reporte || !this.reporte[this.mesSeleccionado]) return;
    
    const datosMes = this.reporte[this.mesSeleccionado];
    const etiqueta = datosMes.etiqueta;
    
    let csvContent = "data:text/csv;charset=utf-8,\uFEFF"; // BOM para Excel
    csvContent += "Reporte Económico BJJFIT\r\n";
    csvContent += `Mes:,${etiqueta}\r\n`;
    csvContent += `Ingresos Totales:,${datosMes.total} EUR\r\n`;
    csvContent += `Usuarios Activos (contabilizados):,${datosMes.usuarios_activos}\r\n`;
    csvContent += `Usuarios Familiares:,${datosMes.usuarios_familiares}\r\n`;
    csvContent += "\r\n";
    
    csvContent += "Desglose por Plan\r\n";
    csvContent += "Plan,Cantidad,Subtotal (EUR)\r\n";
    
    if (datosMes.desglose && datosMes.desglose.length > 0) {
      datosMes.desglose.forEach((d: any) => {
        csvContent += `${d.plan},${d.cantidad},${d.ingresos}\r\n`;
      });
    } else {
      csvContent += "Sin datos de planes para este mes.,,\r\n";
    }

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `reporte_ingresos_${etiqueta.replace(' ', '_')}.csv`);
    document.body.appendChild(link); // Requerido para Firefox
    link.click();
    document.body.removeChild(link);
  }
}
