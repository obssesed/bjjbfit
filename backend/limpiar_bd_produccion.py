"""
Script para limpiar la base de datos de prueba antes de la importacion real.
Conserva: superusuario 'obssesed' y todos los Planes existentes.
Elimina: Deportistas de prueba, Reservas, Clases, Plantillas, Notificaciones, Solicitudes de reseteo.
"""
import os
import sys
import django

# Configuracion Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from usuarios.models import Deportista, SolicitudReseteoPassword, Notificacion, Plan
from reservas.models import ClaseBJJ, PlantillaClase, Reserva


def limpiar():
    """Elimina todos los datos de prueba, conservando obssesed y los planes."""
    
    print("=" * 60)
    print("  LIMPIEZA DE BASE DE DATOS - BJJBFIT")
    print("=" * 60)
    
    # 1. Verificar que obssesed existe antes de proceder
    try:
        admin = Deportista.objects.get(username='obssesed')
        print(f"\n[OK] Admin 'obssesed' encontrado (ID={admin.id}, is_staff={admin.is_staff})")
    except Deportista.DoesNotExist:
        print("\n[ERROR] No se encontro el usuario 'obssesed'. Abortando.")
        return
    
    # 2. Eliminar Reservas
    num_reservas = Reserva.objects.count()
    Reserva.objects.all().delete()
    print(f"[DEL] Reservas eliminadas: {num_reservas}")
    
    # 3. Eliminar Clases
    num_clases = ClaseBJJ.objects.count()
    ClaseBJJ.objects.all().delete()
    print(f"[DEL] Clases eliminadas: {num_clases}")
    
    # 4. Eliminar Plantillas
    num_plantillas = PlantillaClase.objects.count()
    PlantillaClase.objects.all().delete()
    print(f"[DEL] Plantillas eliminadas: {num_plantillas}")
    
    # 5. Eliminar Notificaciones
    num_notificaciones = Notificacion.objects.count()
    Notificacion.objects.all().delete()
    print(f"[DEL] Notificaciones eliminadas: {num_notificaciones}")
    
    # 6. Eliminar Solicitudes de Reseteo
    num_solicitudes = SolicitudReseteoPassword.objects.count()
    SolicitudReseteoPassword.objects.all().delete()
    print(f"[DEL] Solicitudes de reseteo eliminadas: {num_solicitudes}")
    
    # 7. Eliminar todos los Deportistas excepto obssesed
    deportistas_a_borrar = Deportista.objects.exclude(username='obssesed')
    num_deportistas = deportistas_a_borrar.count()
    deportistas_a_borrar.delete()
    print(f"[DEL] Deportistas eliminados: {num_deportistas}")
    
    # 8. Verificar estado final
    print("\n" + "=" * 60)
    print("  ESTADO FINAL")
    print("=" * 60)
    print(f"  Deportistas restantes: {Deportista.objects.count()}")
    for d in Deportista.objects.all():
        print(f"    - {d.username} (staff={d.is_staff})")
    print(f"  Planes conservados: {Plan.objects.count()}")
    for p in Plan.objects.all():
        print(f"    - {p.nombre} ({p.categoria_edad}, {p.precio_base} EUR)")
    print(f"  Reservas: {Reserva.objects.count()}")
    print(f"  Clases: {ClaseBJJ.objects.count()}")
    print(f"  Notificaciones: {Notificacion.objects.count()}")
    print("\n[OK] Limpieza completada.")


if __name__ == '__main__':
    confirmacion = input("ATENCION: Esto BORRARA todos los datos de prueba. Escribe 'SI' para confirmar: ")
    if confirmacion.strip().upper() == 'SI':
        limpiar()
    else:
        print("Operacion cancelada.")
