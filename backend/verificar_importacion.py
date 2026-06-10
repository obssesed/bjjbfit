"""Verificacion rapida de los datos importados."""
import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from usuarios.models import Deportista
from django.db.models import Count

total = Deportista.objects.count()
admin_count = Deportista.objects.filter(is_staff=True).count()
no_admin = Deportista.objects.filter(is_staff=False).count()
print(f'Total usuarios: {total}')
print(f'Admin (staff): {admin_count}')
print(f'Deportistas: {no_admin}')

print('\nSin sexo:')
for d in Deportista.objects.filter(sexo__isnull=True, is_staff=False):
    print(f'  {d.username} - {d.first_name} {d.last_name}')

print('\nCon padre_tutor:')
for d in Deportista.objects.filter(padre_tutor__isnull=False):
    print(f'  {d.first_name} {d.last_name} -> padre: {d.padre_tutor.first_name} {d.padre_tutor.last_name}')

print('\nDistribucion por categoria de plan:')
qs = Deportista.objects.filter(is_staff=False).values('tipo_plan__categoria_edad').annotate(c=Count('id'))
for item in qs:
    cat = item['tipo_plan__categoria_edad']
    cnt = item['c']
    print(f'  {cat}: {cnt}')

cambio_pwd = Deportista.objects.filter(is_staff=False, requiere_cambio_password=True).count()
plan_inactivo = Deportista.objects.filter(is_staff=False, plan_activo=False).count()
print(f'\nTodos con requiere_cambio_password=True: {cambio_pwd}')
print(f'Todos con plan_activo=False: {plan_inactivo}')

# Login test
from django.contrib.auth import authenticate
user = authenticate(username='aaron.montero', password='BjjbFit2026!')
if user:
    print(f'\n[LOGIN TEST] Login OK para aaron.montero (requiere_cambio={user.requiere_cambio_password})')
else:
    print('\n[LOGIN TEST] Login FALLIDO para aaron.montero')
