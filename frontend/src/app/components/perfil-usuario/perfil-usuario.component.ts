import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService, PerfilDeportista } from '../../services/auth.service';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-perfil-usuario',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './perfil-usuario.component.html',
  styleUrls: ['./perfil-usuario.component.css']
})
export class PerfilUsuarioComponent implements OnInit {
  perfil: PerfilDeportista | null = null;
  cargando: boolean = true;
  guardando: boolean = false;
  mensajeResultado: string | null = null;
  mensajeError: boolean = false;

  // Hijos editables
  hijosEditData: any[] = [];

  // Campos editables
  editData = {
    email: '',
    telefono: '',
    nif: '',
    fecha_nacimiento: '',
    sexo: '',
    cuenta_bancaria: '',
    metodo_pago: ''
  };

  // Nuevo hijo
  mostrarFormNuevoHijo: boolean = false;
  nuevoHijo = {
    first_name: '',
    last_name: '',
    fecha_nacimiento: '',
    sexo: '',
    guardando: false
  };

  constructor(private authService: AuthService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.cargarDatos();
  }

  cargarDatos() {
    this.cargando = true;
    this.authService.me().subscribe({
      next: (data) => {
        this.perfil = data;
        this.editData = {
          email: data.email || '',
          telefono: data.telefono || '',
          nif: data.nif || '',
          fecha_nacimiento: data.fecha_nacimiento || '',
          sexo: data.sexo || '',
          cuenta_bancaria: data.cuenta_bancaria || '',
          metodo_pago: data.metodo_pago || 'EFECTIVO'
        };

        // Preparar datos de hijos
        this.hijosEditData = (data.hijos_a_cargo || []).map((h: any) => ({
          ...h,
          edit_email: h.email || '',
          edit_telefono: h.telefono || '',
          edit_nif: h.nif || '',
          edit_fecha_nacimiento: h.fecha_nacimiento || '',
          edit_sexo: h.sexo || ''
        }));

        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al cargar perfil', err);
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  guardar() {
    if (this.editData.metodo_pago === 'CUENTA' && !this.editData.cuenta_bancaria) {
      this.mensajeResultado = '❌ Debes indicar una cuenta bancaria para la domiciliación.';
      this.mensajeError = true;
      this.cdr.detectChanges();
      return;
    }

    this.guardando = true;
    this.mensajeResultado = null;
    this.cdr.detectChanges();

    this.authService.actualizarPerfil(this.editData).subscribe({
      next: (updated) => {
        this.perfil = updated;
        this.guardando = false;
        this.mensajeResultado = '✔️ Perfil actualizado correctamente.';
        this.mensajeError = false;
        this.cdr.detectChanges();

        setTimeout(() => {
          this.mensajeResultado = null;
          this.cdr.detectChanges();
        }, 4000);
      },
      error: (err) => {
        console.error('Error al actualizar perfil', err);
        this.guardando = false;
        this.mensajeResultado = '❌ Error al actualizar los datos.';
        this.mensajeError = true;
        this.cdr.detectChanges();
      }
    });
  }

  guardarHijo(hijo: any) {
    hijo.guardando = true;
    this.mensajeResultado = null;
    this.cdr.detectChanges();

    const payload = {
      email: hijo.edit_email,
      telefono: hijo.edit_telefono,
      nif: hijo.edit_nif,
      fecha_nacimiento: hijo.edit_fecha_nacimiento,
      sexo: hijo.edit_sexo
    };

    this.authService.actualizarPerfilHijo(hijo.id, payload).subscribe({
      next: () => {
        hijo.guardando = false;
        this.mensajeResultado = `✔️ Perfil de ${hijo.first_name} actualizado.`;
        this.mensajeError = false;
        this.cdr.detectChanges();

        setTimeout(() => {
          this.mensajeResultado = null;
          this.cdr.detectChanges();
        }, 4000);
      },
      error: (err) => {
        console.error('Error al actualizar perfil del hijo', err);
        hijo.guardando = false;
        this.mensajeResultado = `❌ Error al actualizar datos de ${hijo.first_name}.`;
        this.mensajeError = true;
        this.cdr.detectChanges();
      }
    });
  }

  toggleFormNuevoHijo() {
    this.mostrarFormNuevoHijo = !this.mostrarFormNuevoHijo;
  }

  crearHijo() {
    this.nuevoHijo.guardando = true;
    this.mensajeResultado = null;
    this.cdr.detectChanges();

    const payload = {
      first_name: this.nuevoHijo.first_name,
      last_name: this.nuevoHijo.last_name,
      fecha_nacimiento: this.nuevoHijo.fecha_nacimiento,
      sexo: this.nuevoHijo.sexo
    };

    this.authService.anadirHijo(payload).subscribe({
      next: (res) => {
        this.nuevoHijo.guardando = false;
        this.mostrarFormNuevoHijo = false;
        this.mensajeResultado = `✔️ Perfil del menor creado correctamente.`;
        this.mensajeError = false;
        // Reiniciamos el form
        this.nuevoHijo = { first_name: '', last_name: '', fecha_nacimiento: '', sexo: '', guardando: false };
        
        // Recargamos el perfil para que aparezca en la lista
        this.cargarDatos();
        
        setTimeout(() => {
          this.mensajeResultado = null;
          this.cdr.detectChanges();
        }, 4000);
      },
      error: (err) => {
        console.error('Error al crear perfil del hijo', err);
        this.nuevoHijo.guardando = false;
        const errMsg = err.error?.error || 'Error al añadir el perfil del menor.';
        this.mensajeResultado = `❌ ${errMsg}`;
        this.mensajeError = true;
        this.cdr.detectChanges();
      }
    });
  }
}
