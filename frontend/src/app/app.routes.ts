import { Routes } from '@angular/router';
import { ListaClasesComponent } from './components/lista-clases/lista-clases.component';
import { LoginComponent } from './components/login/login.component';
import { RegistroComponent } from './components/registro/registro.component';
import { PerfilUsuarioComponent } from './components/perfil-usuario/perfil-usuario.component';
import { MiPerfilComponent } from './components/mi-perfil/mi-perfil.component';
import { AuthGuard } from './guards/auth.guard';
import { Backoffice } from './components/backoffice/backoffice/backoffice';
import { PanelUsuarios } from './components/backoffice/panel-usuarios/panel-usuarios';
import { PanelPlanes } from './components/backoffice/panel-planes/panel-planes';
import { PanelProgramacion } from './components/backoffice/panel-programacion/panel-programacion';
import { PanelReportesComponent } from './components/backoffice/panel-reportes/panel-reportes';
import { PanelNotificacionesComponent } from './components/backoffice/panel-notificaciones/panel-notificaciones';
import { PanelReseteoPasswordComponent } from './components/backoffice/panel-reseteo-password/panel-reseteo-password';

import { HomeComponent } from './components/home/home.component';
import { CambioPasswordComponent } from './components/cambio-password/cambio-password';

export const routes: Routes = [
  { path: 'cambio-password', component: CambioPasswordComponent, canActivate: [AuthGuard] },
  { path: 'home', component: HomeComponent, canActivate: [AuthGuard] },
  { path: 'clases', component: ListaClasesComponent },
  { path: '', redirectTo: 'clases', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'registro', component: RegistroComponent },
  { path: 'mi-perfil', component: PerfilUsuarioComponent, canActivate: [AuthGuard] },
  { path: 'mis-reservas', component: MiPerfilComponent, canActivate: [AuthGuard] },
  { 
    path: 'backoffice', 
    component: Backoffice, 
    canActivate: [AuthGuard],
    children: [
      { path: 'usuarios', component: PanelUsuarios },
      { path: 'planes', component: PanelPlanes },
      { path: 'clases', component: PanelProgramacion },
      { path: 'reportes', component: PanelReportesComponent },
      { path: 'notificaciones', component: PanelNotificacionesComponent },
      { path: 'reseteos', component: PanelReseteoPasswordComponent },
      { path: '', redirectTo: 'usuarios', pathMatch: 'full' }
    ]
  },
  { path: '**', redirectTo: 'clases' }
];
