import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const AdminGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Verificar si el usuario tiene privilegios de administrador (is_staff)
  if (authService.isStaff$.value) {
    return true;
  }

  // Redirigir al Home si no tiene privilegios de administrador
  return router.createUrlTree(['/home']);
};
