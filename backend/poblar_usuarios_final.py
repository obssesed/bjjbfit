import os
import django
import random
from datetime import datetime, timedelta, date

# Configuracion de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import Deportista, Plan
from reservas.models import ClaseBJJ, Reserva

def limpiar_base_datos():
    print("--- Limpiando base de datos ---")
    # Usuarios a mantener
    usuarios_preservar = ['admin_bjj', 'obssesed31', 'padre_familia']
    
    # Borrar todos los deportistas excepto los indicados
    deportistas_a_borrar = Deportista.objects.exclude(username__in=usuarios_preservar)
    num_borrados = deportistas_a_borrar.count()
    deportistas_a_borrar.delete()
    
    # Limpiar reservas antiguas de los usuarios preservados para empezar de cero
    Reserva.objects.all().delete()
    
    print(f"Se han borrado {num_borrados} usuarios.")

def crear_usuarios_y_clase():
    print("--- Creando 31 usuarios con diferentes perfiles ---")
    
    password_comun = "Bjjfit2026!"
    cinturones = ['Blanco', 'Azul', 'Morado', 'Marrón', 'Negro']
    metodos_pago = ['EFECTIVO', 'CUENTA']
    sexos = ['M', 'F']
    
    # Asegurarnos de que existan planes basicos
    plan_adulto, _ = Plan.objects.get_or_create(nombre="Plan Mensual Adulto", precio_base=60, categoria_edad='ADULTO')
    plan_juvenil, _ = Plan.objects.get_or_create(nombre="Plan Juvenil", precio_base=45, categoria_edad='JUVENIL')
    plan_infantil, _ = Plan.objects.get_or_create(nombre="Plan Infantil", precio_base=40, categoria_edad='INFANTIL')

    usuarios_creados = []
    hoy = date.today()

    # 1. JUVENILES (14-17 años) - 5 usuarios
    for i in range(1, 6):
        username = f"juvenil_{i}"
        user = Deportista.objects.create_user(
            username=username,
            email=f"{username}@bjjfit.com",
            password=password_comun,
            first_name=f"Juvenil",
            last_name=f"Numero {i}",
            nif=f"1234567{i}J",
            fecha_nacimiento=hoy - timedelta(days=365 * random.randint(14, 17)),
            sexo=random.choice(sexos),
            cinturon='Blanco',
            plan_activo=True,
            tipo_plan=plan_juvenil
        )
        usuarios_creados.append(user)

    # 2. ADULTOS SIN HIJOS - 10 usuarios
    for i in range(1, 11):
        username = f"adulto_solo_{i}"
        user = Deportista.objects.create_user(
            username=username,
            email=f"{username}@bjjfit.com",
            password=password_comun,
            first_name=f"Adulto",
            last_name=f"Solitario {i}",
            nif=f"2345678{i}A",
            fecha_nacimiento=hoy - timedelta(days=365 * random.randint(20, 50)),
            sexo=random.choice(sexos),
            cinturon=random.choice(cinturones),
            grados=random.randint(0, 4),
            plan_activo=True,
            tipo_plan=plan_adulto,
            metodo_pago=random.choice(metodos_pago)
        )
        usuarios_creados.append(user)

    # 3. ADULTOS CON HIJOS MENORES (<14) - 5 padres + 5 hijos
    for i in range(1, 6):
        username_padre = f"padre_nino_{i}"
        padre = Deportista.objects.create_user(
            username=username_padre,
            email=f"{username_padre}@bjjfit.com",
            password=password_comun,
            first_name=f"Padre",
            last_name=f"Nino {i}",
            nif=f"3456789{i}P",
            fecha_nacimiento=hoy - timedelta(days=365 * random.randint(35, 45)),
            plan_activo=True,
            tipo_plan=plan_adulto
        )
        usuarios_creados.append(padre)
        
        # El hijo
        username_hijo = f"hijo_menor_{i}"
        hijo = Deportista.objects.create_user(
            username=username_hijo,
            email=f"{username_hijo}@bjjfit.com",
            password=password_comun,
            first_name=f"Hijo",
            last_name=f"Menor {i}",
            fecha_nacimiento=hoy - timedelta(days=365 * random.randint(6, 12)),
            padre_tutor=padre,
            plan_activo=True,
            tipo_plan=plan_infantil
        )
        usuarios_creados.append(hijo)

    # 4. ADULTOS CON HIJOS DE +14 (Juveniles asociados) - 3 padres + 3 juveniles
    for i in range(1, 4):
        username_padre = f"padre_juvenil_{i}"
        padre = Deportista.objects.create_user(
            username=username_padre,
            email=f"{username_padre}@bjjfit.com",
            password=password_comun,
            first_name=f"Padre",
            last_name=f"Juvenil {i}",
            nif=f"4567890{i}P",
            fecha_nacimiento=hoy - timedelta(days=365 * random.randint(40, 55)),
            plan_activo=True,
            tipo_plan=plan_adulto
        )
        usuarios_creados.append(padre)
        
        # El hijo que ya tiene 14 o 15 años
        username_hijo = f"hijo_mayor_{i}"
        hijo = Deportista.objects.create_user(
            username=username_hijo,
            email=f"{username_hijo}@bjjfit.com",
            password=password_comun,
            first_name=f"Hijo",
            last_name=f"Mayor {i}",
            fecha_nacimiento=hoy - timedelta(days=365 * 15), 
            padre_tutor=padre,
            plan_activo=True,
            tipo_plan=plan_juvenil
        )
        usuarios_creados.append(hijo)

    # CREAR CLASE PARA TEST DE LISTA DE ESPERA
    print("--- Creando clase de test para manana ---")
    manana = datetime.now() + timedelta(days=1)
    manana_clase = manana.replace(hour=19, minute=0, second=0, microsecond=0)
    
    clase_test = ClaseBJJ.objects.create(
        titulo="Clase Especial Lista de Espera",
        descripcion="Clase diseñada para testear el aforo y la cola automatica.",
        fecha_hora_inicio=manana_clase,
        fecha_hora_fin=manana_clase + timedelta(minutes=90),
        capacidad_maxima=20, 
        icono="Fuego",
        categoria_acceso='ADULTO'
    )

    # RESERVAR PARA LOS 31 USUARIOS
    print(f"--- Reservando clase para los {len(usuarios_creados)} usuarios ---")
    for user in usuarios_creados:
        estado = 'CONFIRMADA'
        if clase_test.plazas_ocupadas() >= clase_test.capacidad_maxima:
            estado = 'ESPERA'
            
        Reserva.objects.create(
            deportista=user,
            clase=clase_test,
            estado=estado
        )

    print("\n--- Proceso completado con exito ---")
    print(f"Password comun: {password_comun}")
    print(f"Usuarios creados: {len(usuarios_creados)}")
    print(f"Clase de Test: '{clase_test.titulo}' a las 19:00h.")

if __name__ == "__main__":
    limpiar_base_datos()
    crear_usuarios_y_clase()
