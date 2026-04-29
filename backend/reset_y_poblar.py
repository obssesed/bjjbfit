import os
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from usuarios.models import Deportista

def reset_y_poblar():
    print("--- Iniciando Reset de Usuarios ---")
    
    # 1. Borrar todos excepto obssesed
    admin_username = "obssesed"
    Deportista.objects.exclude(username=admin_username).delete()
    print(f"Limpieza completada. Solo queda el usuario: {admin_username}")

    # 2. Crear Perfiles
    
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
        tipo_plan="ADULTO",
        es_familiar=True
    )
    
    hijo1 = Deportista.objects.create_user(
        username="hijo_juan",
        email="hijo1@test.com",
        password="password123",
        first_name="Juan",
        last_name="García",
        nif="11111111A", # Comparte NIF del padre
        sexo="M",
        fecha_nacimiento=date(2015, 8, 10),
        telefono="600111222",
        cinturon="Gris",
        grados=1,
        padre_tutor=padre,
        plan_activo=True,
        tipo_plan="INFANTIL"
    )

    hijo2 = Deportista.objects.create_user(
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
        tipo_plan="INFANTIL"
    )
    print("Creada familia García (Padre + 2 Hijos)")

    # --- ADULTA INDIVIDUAL (ACTIVA) ---
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
        tipo_plan="ADULTO"
    )

    # --- JUVENIL (ACTIVO) ---
    Deportista.objects.create_user(
        username="marcos_juvenil",
        email="marcos@test.com",
        password="password123",
        first_name="Marcos",
        last_name="López",
        nif="33333333C",
        sexo="M",
        fecha_nacimiento=date(2009, 6, 30), # 15 años
        telefono="655666777",
        cinturon="Amarillo",
        grados=3,
        plan_activo=True,
        tipo_plan="JUVENIL"
    )

    # --- PENDIENTE (ALTA NUEVA) ---
    Deportista.objects.create_user(
        username="nuevo_alumno",
        email="nuevo@test.com",
        password="password123",
        first_name="Pablo",
        last_name="Sanz",
        nif="44444444D",
        sexo="M",
        fecha_nacimiento=date(1995, 1, 1),
        telefono="677888999",
        cinturon="Blanco",
        grados=0,
        plan_activo=False,
        tipo_plan=None # Sin plan = Pendiente de activación
    )

    # --- INACTIVO (BAJA) ---
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
        tipo_plan="ADULTO" # Tiene plan asignado pero plan_activo=False = Baja
    )


    print("--- Población finalizada con éxito ---")

if __name__ == "__main__":
    reset_y_poblar()
