import os
import django
import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from reservas.models import ClaseBJJ

start_date = timezone.now().date()
end_date = start_date + datetime.timedelta(days=30)

# Delete future classes to recreate them cleanly
ClaseBJJ.objects.filter(fecha_hora_inicio__gte=timezone.now()).delete()

current = start_date
count = 0
while current <= end_date:
    if current.weekday() < 5:  # Monday to Friday = 0 to 4
        # Morning
        dt_m = timezone.make_aware(datetime.datetime.combine(current, datetime.time(10, 0)))
        ClaseBJJ.objects.create(titulo="BJJ Fundamentos", descripcion="Clase de la mañana", fecha_hora_inicio=dt_m, capacidad_maxima=20)
        
        # Evening
        dt_e = timezone.make_aware(datetime.datetime.combine(current, datetime.time(19, 0)))
        ClaseBJJ.objects.create(titulo="BJJ Competición", descripcion="Clase de tarde", fecha_hora_inicio=dt_e, capacidad_maxima=30)
        count += 2
    current += datetime.timedelta(days=1)

print(f"Éxito. Creadas {count} clases de BJJ de Lunes a Viernes para el próximo mes.")
