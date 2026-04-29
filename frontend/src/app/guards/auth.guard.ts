import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const AuthGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isLoggedIn()) {
    return true;
  }

  // Verificar en localStorage directamente como backup rápido en SSR/CSR mix
  if (typeof window !== 'undefined' && localStorage.getItem('access_token')) {
    return true;
  }

  return router.createUrlTree(['/login']);
};
