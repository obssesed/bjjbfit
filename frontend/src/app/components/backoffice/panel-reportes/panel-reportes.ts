import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../services/auth.service';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartOptions } from 'chart.js';

@Component({
  selector: 'app-panel-reportes',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  templateUrl: './panel-reportes.html',
  styleUrls: ['./panel-reportes.css']
})
export class PanelReportesComponent implements OnInit {
  reporte: any = null;
  reporteAnual: any[] = [];
  loading: boolean = true;
  error: string | null = null;
  mesSeleccionado: string = 'mes_actual';

  // Configuración Chart Sexo (Donut)
  pieChartData: ChartConfiguration<'doughnut'>['data'] | null = null;
  pieChartOptions: ChartOptions<'doughnut'> = {
    responsive: true,
    plugins: {
      legend: { position: 'bottom', labels: { color: '#e2e8f0' } }
    }
  };

  // Configuración Chart Planes (Bar)
  barChartData: ChartConfiguration<'bar'>['data'] | null = null;
  barChartOptions: ChartOptions<'bar'> = {
    responsive: true,
    plugins: {
      legend: { display: false }
    },
    scales: {
      y: { beginAtZero: true, ticks: { color: '#cbd5e1' } },
      x: { ticks: { color: '#cbd5e1' } }
    }
  };

  // Configuración Chart Anual (Line)
  lineChartData: ChartConfiguration<'line'>['data'] | null = null;
  lineChartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top', labels: { color: '#e2e8f0' } }
    },
    scales: {
      y: { beginAtZero: true, ticks: { color: '#cbd5e1' } },
      x: { ticks: { color: '#cbd5e1' } }
    }
  };

  constructor(private authService: AuthService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.cargarReporte();
  }

  cargarReporte() {
    this.loading = true;
    this.error = null;
    
    // Petición al reporte de meses
    this.authService.getReporteIngresos().subscribe({
      next: (data) => {
        this.reporte = data;
        this.actualizarGraficosMes();
        this.checkCargaCompleta();
      },
      error: (err) => {
        console.error('Error al cargar reporte', err);
        this.error = 'No se pudo cargar el reporte económico.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });

    // Petición al reporte anual
    this.authService.getReporteAnual().subscribe({
      next: (data) => {
        this.reporteAnual = data;
        this.generarGraficoAnual();
        this.checkCargaCompleta();
      },
      error: (err) => console.error('Error al cargar reporte anual', err)
    });
  }

  checkCargaCompleta() {
    if (this.reporte && this.reporteAnual.length > 0) {
      this.loading = false;
      this.cdr.detectChanges();
    }
  }

  seleccionarMes(mesKey: string) {
    this.mesSeleccionado = mesKey;
    this.actualizarGraficosMes();
    this.cdr.detectChanges();
  }

  actualizarGraficosMes() {
    if (!this.reporte) return;
    const datosMes = this.reporte[this.mesSeleccionado];
    if (!datosMes) return;

    // Actualizar Pie Chart (Sexo)
    if (datosMes.desglose_sexo) {
      this.pieChartData = {
        labels: datosMes.desglose_sexo.map((d: any) => d.sexo),
        datasets: [{
          data: datosMes.desglose_sexo.map((d: any) => d.cantidad),
          backgroundColor: ['#3b82f6', '#ec4899', '#94a3b8'],
          hoverBackgroundColor: ['#60a5fa', '#f472b6', '#cbd5e1'],
          borderWidth: 0
        }]
      };
    }

    // Actualizar Bar Chart (Planes)
    if (datosMes.desglose) {
      this.barChartData = {
        labels: datosMes.desglose.map((d: any) => d.plan),
        datasets: [{
          label: 'Usuarios Activos',
          data: datosMes.desglose.map((d: any) => d.cantidad),
          backgroundColor: '#10b981',
          hoverBackgroundColor: '#34d399',
          borderRadius: 4
        }]
      };
    }
  }

  generarGraficoAnual() {
    if (!this.reporteAnual || this.reporteAnual.length === 0) return;

    const labels = this.reporteAnual.map(m => m.etiqueta.split(' ')[0]); // Solo el mes para que quepa bien
    const datosActivos = this.reporteAnual.map(m => m.activos);
    const datosIngresos = this.reporteAnual.map(m => m.total);

    this.lineChartData = {
      labels: labels,
      datasets: [
        {
          label: 'Usuarios Activos',
          data: datosActivos,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.2)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          yAxisID: 'y'
        },
        {
          label: 'Ingresos (€)',
          data: datosIngresos,
          borderColor: '#f59e0b',
          backgroundColor: 'transparent',
          borderWidth: 3,
          borderDash: [5, 5],
          tension: 0.4,
          yAxisID: 'y1'
        }
      ]
    };

    // Ajustar opciones para doble eje Y
    this.lineChartOptions = {
      ...this.lineChartOptions,
      scales: {
        x: { ticks: { color: '#cbd5e1' } },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          ticks: { color: '#3b82f6' },
          title: { display: true, text: 'Usuarios', color: '#cbd5e1' }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { color: '#f59e0b' },
          title: { display: true, text: 'Ingresos (€)', color: '#cbd5e1' }
        }
      }
    };
  }

  exportarCSV() {
    if (!this.reporte || !this.reporte[this.mesSeleccionado]) return;
    
    const datosMes = this.reporte[this.mesSeleccionado];
    const etiqueta = datosMes.etiqueta;
    
    let csvContent = "data:text/csv;charset=utf-8,\uFEFF";
    csvContent += "Reporte Económico BJJFIT\r\n";
    csvContent += `Mes:,${etiqueta}\r\n`;
    csvContent += `Ingresos Totales:,${datosMes.total} EUR\r\n`;
    csvContent += `Usuarios Activos:,${datosMes.usuarios_activos}\r\n`;
    csvContent += `Usuarios Familiares:,${datosMes.usuarios_familiares}\r\n\r\n`;
    
    csvContent += "Desglose por Plan\r\n";
    csvContent += "Plan,Cantidad,Subtotal (EUR)\r\n";
    if (datosMes.desglose && datosMes.desglose.length > 0) {
      datosMes.desglose.forEach((d: any) => {
        csvContent += `${d.plan},${d.cantidad},${d.ingresos}\r\n`;
      });
    } else {
      csvContent += "Sin datos.,,\r\n";
    }

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `reporte_ingresos_${etiqueta.replace(' ', '_')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}
