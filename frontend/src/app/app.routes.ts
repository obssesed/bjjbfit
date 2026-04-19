import { Routes } from '@angular/router';
import { ListaClasesComponent } from './components/lista-clases/lista-clases.component';
import { LoginComponent } from './components/login/login.component';
import { RegistroComponent } from './components/registro/registro.component';
import { MiPerfilComponent } from './components/mi-perfil/mi-perfil.component';

export const routes: Routes = [
  { path: '', component: ListaClasesComponent },
  { path: 'login', component: LoginComponent },
  { path: 'registro', component: RegistroComponent },
  { path: 'mis-reservas', component: MiPerfilComponent }
];
