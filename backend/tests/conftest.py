import pytest
from django.utils import timezone
from usuarios.models import Deportista
from reservas.models import ClaseBJJ

@pytest.fixture
def deportista_padre(db):
    """Crea un deportista adulto con plan activo."""
    return Deportista.objects.create_user(
        username="padre1",
        email="padre1@test.com",
        password="password_secreta",
        plan_activo=True,
        nif="11111111A",
        fecha_nacimiento="1985-05-15",
        sexo="M"
    )

@pytest.fixture
def deportista_padre_sin_plan(db):
    """Crea un deportista adulto sin plan activo."""
    return Deportista.objects.create_user(
        username="padresn",
        email="padresn@test.com",
        password="password_secreta",
        plan_activo=False
    )

@pytest.fixture
def deportista_hijo(db, deportista_padre):
    """Crea un deportista menor tutelado por deportista_padre."""
    return Deportista.objects.create_user(
        username="hijo1",
        email="hijo1@test.com",
        password="password_secreta",
        plan_activo=True,
        padre_tutor=deportista_padre,
        nif="11111111A" # Misma id que el padre
    )

@pytest.fixture
def clase_con_hueco(db):
    """Crea una clase con 2 plazas para los tests."""
    inicio = timezone.now() + timezone.timedelta(days=1)
    fin = inicio + timezone.timedelta(hours=1)
    return ClaseBJJ.objects.create(
        titulo="Clase Test Con Hueco",
        fecha_hora_inicio=inicio,
        fecha_hora_fin=fin,
        capacidad_maxima=2
    )

@pytest.fixture
def deportista_adulto_soltero(db):
    return Deportista.objects.create_user(
        username="adultosolo",
        email="solo@test.com",
        password="password_secreta",
        plan_activo=True
    )

@pytest.fixture
def clase_pasada(db):
    inicio = timezone.now() - timezone.timedelta(days=1)
    return ClaseBJJ.objects.create(
        titulo="Clase Pasada",
        fecha_hora_inicio=inicio,
        capacidad_maxima=2
    )

@pytest.fixture
def clase_inminente(db):
    inicio = timezone.now() + timezone.timedelta(minutes=10)
    return ClaseBJJ.objects.create(
        titulo="Clase Inminente",
        fecha_hora_inicio=inicio,
        capacidad_maxima=2
    )
