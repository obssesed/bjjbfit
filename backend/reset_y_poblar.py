import os
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from usuarios.models import Deportista, Plan

def reset_y_poblar():
    print("--- Iniciando Reset de Usuarios y Planes ---")
    
    # 1. Asegurar Admin y borrar otros
    admin_username = "obssesed"
    if not Deportista.objects.filter(username=admin_username).exists():
        Deportista.objects.create_superuser(
            username=admin_username,
            email="admin@bjjfit.com",
            password="admin1234"
        )
        print(f"Superusuario {admin_username} creado.")
    
    Deportista.objects.exclude(username=admin_username).delete()
    
    # 2. Borrar y recrear planes
    Plan.objects.all().delete()
    
    plan_adulto = Plan.objects.create(
        nombre="Adulto",
        precio_base=70.00,
        beneficios="Todas las actividades excepto las de infantiles y juveniles",
        categoria_edad="ADULTO"
    )
    
    plan_juvenil = Plan.objects.create(
        nombre="Juvenil",
        precio_base=50.00,
        beneficios="Solo las actividades juveniles",
        categoria_edad="JUVENIL"
    )
    
    plan_infantil = Plan.objects.create(
        nombre="Infantil",
        precio_base=40.00,
        beneficios="Solo las actividades infantiles",
        categoria_edad="INFANTIL"
    )
    
    print("Planes base creados con éxito.")

    # 3. Crear Perfiles de prueba
    
    # --- PADRE CON HIJOS ---
    padre = Deportista.objects.create_user(
        username="padre_familia",
        email="padre@test.com",
        password="password123",
        first_name="Ricardo",
        last_name="García",
        nif="11111111A",
        sexo="M",
        fecha_nacimiento=date(1985, 5, 20),
        telefono="600111222",
        cinturon="Morado",
        grados=2,
        plan_activo=True,
        tipo_plan=plan_adulto,
        es_familiar=True
    )
    
    Deportista.objects.create_user(
        username="hijo_juan",
        email="hijo1@test.com",
        password="password123",
        first_name="Juan",
        last_name="García",
        nif="11111111A",
        sexo="M",
        fecha_nacimiento=date(2015, 8, 10),
        telefono="600111222",
        cinturon="Gris",
        grados=1,
        padre_tutor=padre,
        plan_activo=True,
        tipo_plan=plan_infantil
    )

    Deportista.objects.create_user(
        username="hija_sofia",
        email="hija2@test.com",
        password="password123",
        first_name="Sofia",
        last_name="García",
        nif="11111111A",
        sexo="F",
        fecha_nacimiento=date(2018, 3, 15),
        telefono="600111222",
        cinturon="Blanco",
        grados=0,
        padre_tutor=padre,
        plan_activo=True,
        tipo_plan=plan_infantil
    )

    # --- ADULTA INDIVIDUAL ---
    Deportista.objects.create_user(
        username="elena_bjj",
        email="elena@test.com",
        password="password123",
        first_name="Elena",
        last_name="Méndez",
        nif="22222222B",
        sexo="F",
        fecha_nacimiento=date(1992, 11, 2),
        telefono="622333444",
        cinturon="Azul",
        grados=4,
        plan_activo=True,
        tipo_plan=plan_adulto
    )

    # --- JUVENIL ---
    Deportista.objects.create_user(
        username="marcos_juvenil",
        email="marcos@test.com",
        password="password123",
        first_name="Marcos",
        last_name="López",
        nif="33333333C",
        sexo="M",
        fecha_nacimiento=date(2009, 6, 30),
        telefono="655666777",
        cinturon="Amarillo",
        grados=3,
        plan_activo=True,
        tipo_plan=plan_juvenil
    )

    # --- INACTIVO ---
    Deportista.objects.create_user(
        username="ex_alumno",
        email="baja@test.com",
        password="password123",
        first_name="Marta",
        last_name="Ruiz",
        nif="55555555E",
        sexo="F",
        fecha_nacimiento=date(1988, 4, 12),
        telefono="688999000",
        cinturon="Azul",
        grados=2,
        plan_activo=False,
        tipo_plan=plan_adulto
    )

    print("--- Población finalizada con éxito ---")

if __name__ == "__main__":
    reset_y_poblar()

if __name__ == "__main__":
    reset_y_poblar()
