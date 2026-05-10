import os
import django
import random
from datetime import datetime, timedelta

# Configuracion de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.utils import timezone
from usuarios.models import Deportista
from reservas.models import ClaseBJJ, Reserva

def simular_espera_hoy():
    print("--- Simulando clase llena para HOY ---")
    
    # 1. Crear una clase para dentro de 1 hora
    hora_inicio = timezone.now() + timedelta(hours=1)
    # Redondear a la hora exacta para que quede bonito
    hora_inicio = hora_inicio.replace(minute=0, second=0, microsecond=0)
    
    clase = ClaseBJJ.objects.create(
        titulo="BJJ Fundamentos (FULL TEST)",
        descripcion="Clase de prueba para ver el comportamiento de la lista de espera en tiempo real.",
        fecha_hora_inicio=hora_inicio,
        fecha_hora_fin=hora_inicio + timedelta(minutes=90),
        capacidad_maxima=10,
        icono="🥋",
        categoria_acceso='ADULTO'
    )
    
    # 2. Obtener 10 usuarios aleatorios para llenar la clase (que no sean los principales)
    usuarios_relleno = list(Deportista.objects.exclude(username__in=['obssesed31', 'padre_familia', 'admin_bjj']).order_by('?')[:10])
    
    print(f"Llenando clase '{clase.titulo}' con 10 usuarios...")
    for u in usuarios_relleno:
        Reserva.objects.create(
            deportista=u,
            clase=clase,
            estado='CONFIRMADA'
        )
    
    # 3. Meter a obssesed31 y padre_familia en espera
    print("Metiendo a obssesed31 y padre_familia en lista de espera...")
    
    users_espera = Deportista.objects.filter(username__in=['obssesed31', 'padre_familia'])
    for u in users_espera:
        Reserva.objects.create(
            deportista=u,
            clase=clase,
            estado='ESPERA'
        )

    print("\n✅ OK: Clase creada y llena.")
    print(f"ID Clase: {clase.id}")
    print(f"Titulo: {clase.titulo}")
    print(f"Aforo: 10/10 (+ 2 en espera)")
    print(f"Usuarios en espera: obssesed31, padre_familia")

if __name__ == "__main__":
    simular_espera_hoy()
