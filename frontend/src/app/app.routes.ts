import { Routes } from '@angular/router';
import { ListaClasesComponent } from './components/lista-clases/lista-clases.component';
import { LoginComponent } from './components/login/login.component';
import { RegistroComponent } from './components/registro/registro.component';
import { MiPerfilComponent } from './components/mi-perfil/mi-perfil.component';
import { AuthGuard } from './guards/auth.guard';
import { Backoffice } from './components/backoffice/backoffice/backoffice';
import { PanelUsuarios } from './components/backoffice/panel-usuarios/panel-usuarios';

export const routes: Routes = [
  { path: '', component: ListaClasesComponent },
  { path: 'login', component: LoginComponent },
  { path: 'registro', component: RegistroComponent },
  { path: 'mis-reservas', component: MiPerfilComponent, canActivate: [AuthGuard] },
  { 
    path: 'backoffice', 
    component: Backoffice, 
    canActivate: [AuthGuard],
    children: [
      { path: 'usuarios', component: PanelUsuarios },
      { path: '', redirectTo: 'usuarios', pathMatch: 'full' }
    ]
  },
  { path: '**', redirectTo: '' }
];
