import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ClasesService, ClaseBJJ } from '../../services/clases.service';
import { AuthService } from '../../services/auth.service';

interface DiaCalendario {
  nombre: string;
  fechaObj: Date;
  numero: number;
  esHoy: boolean;
  clases: ClaseBJJ[];
}

@Component({
  selector: 'app-lista-clases',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lista-clases.component.html',
  styleUrls: ['./lista-clases.component.css']
})
export class ListaClasesComponent implements OnInit {
  semana: DiaCalendario[] = [];
  cargando: boolean = true;
  error: string | null = null;
  mensajeExito: string | null = null;

  constructor(
    private clasesService: ClasesService, 
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.cargarClases();
  }

  cargarClases() {
    this.clasesService.getClases().subscribe({
      next: (data) => {
        this.construirSemana(data);
        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error cargando las clases', err);
        this.error = 'No se pudo conectar con el servidor de la API.';
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  construirSemana(todasLasClases: ClaseBJJ[]) {
    this.semana = [];
    const hoy = new Date();
    // 1 es Lunes, 7 es Domingo
    const diaActual = hoy.getDay() === 0 ? 7 : hoy.getDay(); 
    
    // Obtener el Lunes de la semana en curso
    const lunes = new Date(hoy);
    lunes.setDate(hoy.getDate() - diaActual + 1);
    
    const nombresDias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

    for (let i = 0; i < 7; i++) {
        const iterDia = new Date(lunes);
        iterDia.setDate(lunes.getDate() + i);
        
        // Comprobar si es el día de hoy exacto
        const esHoy = iterDia.getDate() === hoy.getDate() && iterDia.getMonth() === hoy.getMonth();

        this.semana.push({
            nombre: nombresDias[i],
            numero: iterDia.getDate(),
            fechaObj: iterDia,
            esHoy: esHoy,
            clases: []
        });
    }

    // Filtrar y ordenar clases en su día correspondiente
    todasLasClases.forEach(clase => {
        const claseDate = new Date(clase.fecha_hora_inicio);
        const dayIndex = this.semana.findIndex(d => 
            d.fechaObj.getFullYear() === claseDate.getFullYear() &&
            d.fechaObj.getMonth() === claseDate.getMonth() &&
            d.fechaObj.getDate() === claseDate.getDate()
        );

        if (dayIndex !== -1) {
            this.semana[dayIndex].clases.push(clase);
        }
    });

    // Ordenar cronológicamente dentro de cada día
    this.semana.forEach(dia => {
        dia.clases.sort((a, b) => new Date(a.fecha_hora_inicio).getTime() - new Date(b.fecha_hora_inicio).getTime());
    });
  }

  // Helper para generar formato de ejemplo: "10:00-11:00"
  obtenerFormatoHorario(fechaInicioIso: string): string {
    const inicio = new Date(fechaInicioIso);
    const fin = new Date(inicio);
    fin.setHours(inicio.getHours() + 1); // Asumimos clase de 1 hora

    const fInicio = inicio.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const fFin = fin.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    return `${fInicio} - ${fFin}`;
  }

  // Verifica si una clase ya ha comenzado / pasado
  esClasePasada(fechaInicioIso: string): boolean {
    const ahora = new Date();
    const claseDate = new Date(fechaInicioIso);
    return claseDate.getTime() < ahora.getTime();
  }

  reservar(clase: ClaseBJJ) {
    if (this.esClasePasada(clase.fecha_hora_inicio)) {
      alert("No puedes reservar una clase que ya está en el pasado.");
      return;
    }

    if (!this.authService.isLoggedIn()) {
      // Si no estamos logeados, Angular nos manda al login para no intentar peticiones invalidas
      this.router.navigate(['/login']);
      return;
    }

    // Optimistic Update: Restamos visualmente antes de que conteste el servidor
    // Esto asegura que la interfaz reacciona instantáneamente (0ms de lag)
    clase.plazas_disponibles -= 1;

    this.clasesService.hacerReserva(clase.id).subscribe({
      next: () => {
        this.mensajeExito = "¡Plaza reservada con éxito! Te esperamos en el tatami.";
        setTimeout(() => this.mensajeExito = null, 3000);
      },
      error: (err) => {
        // Rollback visual si el servidor nos dice que hubo un error (ej. ya lo tenía reservado)
        clase.plazas_disponibles += 1;
        alert("Ya tienes esta clase reservada o ha ocurrido un error.");
        console.error(err);
      }
    });
  }
}
