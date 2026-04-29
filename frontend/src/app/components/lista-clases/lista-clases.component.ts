import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ClasesService, ClaseBJJ } from '../../services/clases.service';
import { AuthService, PerfilDeportista } from '../../services/auth.service';

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
  imports: [CommonModule, FormsModule],
  templateUrl: './lista-clases.component.html',
  styleUrls: ['./lista-clases.component.css']
})
export class ListaClasesComponent implements OnInit {
  semana: DiaCalendario[] = [];
  todasLasClases: ClaseBJJ[] = [];
  offsetSemanas: number = 0;
  opcionesSemanas = [
    { valor: 0, etiqueta: 'Semana Actual' },
    { valor: 1, etiqueta: 'Próxima Semana' },
    { valor: 2, etiqueta: 'En 2 Semanas' },
    { valor: 3, etiqueta: 'En 3 Semanas' }
  ];

  cargando: boolean = true;
  error: string | null = null;
  mensajeExito: string | null = null;

  perfilDeportista: PerfilDeportista | null = null;
  showModal: boolean = false;
  claseSeleccionada: ClaseBJJ | null = null;
  asistenteSeleccionado: number = 0;

  misReservasActivas: any[] = [];
  showCancelModal: boolean = false;
  reservaACancelarID: number = 0;
  
  showErrorModal: boolean = false;
  mensajeErrorModal: string = '';

  constructor(
    private clasesService: ClasesService, 
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.cargarClases();
    if (this.authService.isLoggedIn()) {
      this.authService.me().subscribe({
        next: (data) => this.perfilDeportista = data,
        error: (err) => console.error('Error cargando perfil', err)
      });
      this.cargarMisReservas();
    }
  }

  cargarMisReservas() {
    this.clasesService.getMisReservas().subscribe({
      next: (data) => {
        this.misReservasActivas = data.filter(r => r.estado !== 'CANCELADA');
      },
      error: (err) => console.error('Error cargando mis reservas activas', err)
    });
  }

  cargarClases() {
    this.clasesService.getClases().subscribe({
      next: (data) => {
        console.log('DEBUG - Clases cargadas:', data);
        this.todasLasClases = data;
        this.construirSemana();
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

  cambiarSemana() {
    this.offsetSemanas = Number(this.offsetSemanas);
    this.construirSemana();
  }

  construirSemana() {
    this.semana = [];
    const hoy = new Date();
    // 1 es Lunes, 7 es Domingo
    const diaActual = hoy.getDay() === 0 ? 7 : hoy.getDay(); 
    
    // Obtener el Lunes de la semana seleccionada
    const lunes = new Date(hoy);
    lunes.setDate(hoy.getDate() - diaActual + 1 + (this.offsetSemanas * 7));
    
    const nombresDias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

    for (let i = 0; i < 7; i++) {
        const iterDia = new Date(lunes);
        iterDia.setDate(lunes.getDate() + i);
        
        // Comprobar si es el día de hoy exacto
        const esHoy = iterDia.getDate() === hoy.getDate() && iterDia.getMonth() === hoy.getMonth() && iterDia.getFullYear() === hoy.getFullYear();

        this.semana.push({
            nombre: nombresDias[i],
            numero: iterDia.getDate(),
            fechaObj: iterDia,
            esHoy: esHoy,
            clases: []
        });
    }

    // Filtrar y ordenar clases en su día correspondiente
    this.todasLasClases.forEach(clase => {
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

  esClasePasada(fechaInicioIso: string): boolean {
    const ahora = new Date();
    const claseDate = new Date(fechaInicioIso);
    return claseDate.getTime() < ahora.getTime();
  }

  estaAbiertaParaReserva(fechaInicioIso: string): boolean {
    const ahora = new Date();
    const claseDate = new Date(fechaInicioIso);
    const msIn24Hours = 24 * 60 * 60 * 1000;
    
    // Si quedan más de 24 horas para que empiece, aún no está abierta
    if (claseDate.getTime() - ahora.getTime() > msIn24Hours) {
      return false;
    }
    return true;
  }

  // --- LÓGICA DUAL DE BOTONES ---
  getReservasEnClase(claseId: number): any[] {
    return this.misReservasActivas.filter(r => r.clase === claseId);
  }

  puedeCancelar(claseId: number): boolean {
    return this.getReservasEnClase(claseId).length > 0;
  }

  cumpleCategoria(deportista: any, clase: ClaseBJJ): boolean {
    if (!deportista || !deportista.categoria_plan) return true;
    return deportista.categoria_plan === clase.categoria_acceso;
  }

  puedeReservar(claseId: number): boolean {
    if (!this.perfilDeportista) return true;
    
    const claseObj = this.todasLasClases.find(c => c.id === claseId);
    if (!claseObj) return true;

    const perfilesDisponibles: any[] = [this.perfilDeportista];
    if (this.perfilDeportista.hijos_a_cargo) {
      perfilesDisponibles.push(...this.perfilDeportista.hijos_a_cargo);
    }

    return perfilesDisponibles.some(p => 
      this.cumpleCategoria(p, claseObj) && !this.estaInscrito(p.id, claseId)
    );
  }
  estaInscrito(deportistaId: number, claseId: number): boolean {
    const reservas = this.getReservasEnClase(claseId);
    return reservas.some(r => r.deportista === deportistaId);
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

    if (this.perfilDeportista && this.perfilDeportista.hijos_a_cargo && this.perfilDeportista.hijos_a_cargo.length > 0) {
      this.claseSeleccionada = clase;
      
      // Preseleccionar Yo si cumplo categoria y no estoy inscrito
      if (this.cumpleCategoria(this.perfilDeportista, clase) && !this.estaInscrito(this.perfilDeportista.id, clase.id)) {
        this.asistenteSeleccionado = this.perfilDeportista.id;
      } else {
        // Si no, buscar el primer hijo que cumpla y no este inscrito
        const primerHijoValido = this.perfilDeportista.hijos_a_cargo.find(h => 
          this.cumpleCategoria(h, clase) && !this.estaInscrito(h.id, clase.id)
        );
        this.asistenteSeleccionado = primerHijoValido ? primerHijoValido.id : 0;
      }

      this.showModal = true;
    } else {
      this.ejecutarReservaReal(clase);
    }
  }

  cancelarReservaModal() {
    this.showModal = false;
    this.claseSeleccionada = null;
  }

  confirmarReservaModal() {
    this.showModal = false;
    if (this.claseSeleccionada) {
      const targetId = this.asistenteSeleccionado === Number(this.perfilDeportista!.id) ? undefined : this.asistenteSeleccionado;
      this.ejecutarReservaReal(this.claseSeleccionada, targetId);
    }
  }

  ejecutarReservaReal(clase: ClaseBJJ, deportistaId?: number) {
    // Optimistic Update: Solo restamos visualmente si había plaza libre
    let restado = false;
    if (clase.plazas_disponibles > 0) {
      clase.plazas_disponibles -= 1;
      restado = true;
    }

    this.clasesService.hacerReserva(clase.id, deportistaId).subscribe({
      next: (response) => {
        if (response.estado === 'ESPERA') {
          this.mensajeExito = "¡En lista de espera! Te avisaremos si queda algún hueco libre.";
        } else {
          this.mensajeExito = "¡Plaza reservada con éxito! Te esperamos en el tatami.";
        }
        this.cdr.detectChanges();
        setTimeout(() => this.mensajeExito = null, 4000);
        
        // Refrescamos en background para tener datos reales exactos
        setTimeout(() => {
          this.cargarClases();
          this.cargarMisReservas();
        }, 2000);
      },
      error: (err) => {
        // Rollback visual si restamos plaza
        if (restado) {
          clase.plazas_disponibles += 1;
        }

        let msg = "Ha ocurrido un error al intentar reservar.";
        if (err.status === 400 && err.error && err.error.non_field_errors) {
           msg = err.error.non_field_errors[0];
        } else if (err.status === 403) {
           msg = "No tienes permiso para realizar esta acción.";
        } else if (err.error && typeof err.error === 'object' && err.error[0] && typeof err.error[0] === 'string') {
           msg = err.error[0];
        }
        
        this.mensajeErrorModal = msg;
        this.showErrorModal = true;
        console.error(err);
        this.cdr.detectChanges();
      }
    });
  }

  // --- LÓGICA DE CANCELACIÓN EXPRESS ---
  cancelarFrente(clase: ClaseBJJ) {
    if (this.esClasePasada(clase.fecha_hora_inicio)) {
      alert("No puedes cancelar una clase pasada.");
      return;
    }
    if (!this.authService.isLoggedIn()) return;

    const reservasOcupadas = this.getReservasEnClase(clase.id);

    // Activamos siempre el modal rojo bonito, independientemente del número de reservas
    this.claseSeleccionada = clase;
    this.showCancelModal = true;
    
    // Si solo hay una reserva, la pre-seleccionamos automáticamente
    if (reservasOcupadas.length === 1) {
      this.reservaACancelarID = reservasOcupadas[0].id;
    } else {
      this.reservaACancelarID = 0; // Obligamos a clicar si hay varias
    }
    this.cdr.detectChanges();
  }

  cerrarErrorModal() {
    this.showErrorModal = false;
    this.mensajeErrorModal = '';
  }

  cerrarCancelModal() {
    this.showCancelModal = false;
    this.claseSeleccionada = null;
  }

  confirmarCancelModal(reservaId: number) {
    this.showCancelModal = false;
    if (this.claseSeleccionada) {
      this.ejecutarCancelacionReal(reservaId, this.claseSeleccionada);
    }
  }

  ejecutarCancelacionReal(reservaId: number, claseTarget: ClaseBJJ) {
    // Optimistic Update inverso
    claseTarget.plazas_disponibles += 1;

    this.clasesService.cancelarReserva(reservaId).subscribe({
      next: () => {
        this.mensajeExito = "Reserva cancelada correctamente.";
        this.cdr.detectChanges();
        setTimeout(() => this.mensajeExito = null, 4000);
        setTimeout(() => {
          this.cargarClases();
          this.cargarMisReservas();
        }, 1500);
      },
      error: (err) => {
        claseTarget.plazas_disponibles -= 1; // rollback
        let errorMsg = "Ocurrió un error al cancelar.";
        if (err.error && err.error[0] && typeof err.error[0] === 'string') {
           errorMsg = err.error[0];
        } else if (err.error && err.error.detail) {
           errorMsg = err.error.detail;
        }
        this.mensajeErrorModal = errorMsg;
        this.showErrorModal = true;
        this.cdr.detectChanges();
      }
    });
  }
}
