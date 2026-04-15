import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ClasesService, ClaseBJJ } from '../../services/clases.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-lista-clases',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lista-clases.component.html',
  styleUrls: ['./lista-clases.component.css']
})
export class ListaClasesComponent implements OnInit {
  clases: ClaseBJJ[] = [];
  cargando: boolean = true;
  error: string | null = null;
  mensajeExito: string | null = null;

  constructor(
    private clasesService: ClasesService, 
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.cargarClases();
  }

  cargarClases() {
    this.clasesService.getClases().subscribe({
      next: (data) => {
        this.clases = data;
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error cargando las clases', err);
        this.error = 'No se pudo conectar con el servidor de la API.';
        this.cargando = false;
      }
    });
  }

  reservar(clase: ClaseBJJ) {
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
