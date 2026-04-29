import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from usuarios.models import Deportista
from reservas.models import ClaseBJJ, Reserva
from django.utils import timezone

def poblar():
    # Pendientes de alta (Sin plan, sin reservas)
    for i in range(3):
        Deportista.objects.get_or_create(
            username=f"pendiente_{i}",
            defaults={
                "first_name": f"Nuevo",
                "last_name": f"Pupilo {i}",
                "email": f"pend{i}@test.com",
                "plan_activo": False,
                "cinturon": "Blanco"
            }
        )

    # Inactivos / Bajas (Sin plan, con 1 reserva historica)
    c, _ = ClaseBJJ.objects.get_or_create(
        titulo="Clase Histórica para Tests",
        defaults={
            "fecha_hora_inicio": timezone.now() - timezone.timedelta(days=100),
            "fecha_hora_fin": timezone.now() - timezone.timedelta(days=100, hours=-1)
        }
    )

    for i in range(3):
        d, created = Deportista.objects.get_or_create(
            username=f"inactivo_historico_{i}",
            defaults={
                "first_name": f"Mítico",
                "last_name": f"Veterano {i}",
                "email": f"old{i}@test.com",
                "plan_activo": False,
                "cinturon": "Azul"
            }
        )
        if created:
            Reserva.objects.get_or_create(clase=c, deportista=d, estado='CONFIRMADA')

    print("DB Poblada exitosamente.")

if __name__ == "__main__":
    poblar()
