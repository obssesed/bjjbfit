import { Routes } from '@angular/router';
import { ListaClasesComponent } from './components/lista-clases/lista-clases.component';
import { LoginComponent } from './components/login/login.component';

export const routes: Routes = [
  { path: '', component: ListaClasesComponent },
  { path: 'login', component: LoginComponent }
];
