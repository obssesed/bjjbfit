import pytest
from reservas.models import ClaseBJJ, Reserva

@pytest.mark.django_db
def test_si_clase_tiene_reservas_resultado_plazas_disponibles_restan_bien(clase_con_hueco, deportista_padre):
    assert clase_con_hueco.plazas_disponibles() == 2
    Reserva.objects.create(clase=clase_con_hueco, deportista=deportista_padre, estado='CONFIRMADA')
    assert clase_con_hueco.plazas_disponibles() == 1

@pytest.mark.django_db
def test_si_reserva_cancelada_resultado_no_resta_aforo(clase_con_hueco, deportista_padre):
    Reserva.objects.create(clase=clase_con_hueco, deportista=deportista_padre, estado='CANCELADA')
    assert clase_con_hueco.plazas_disponibles() == 2

@pytest.mark.django_db
def test_si_reserva_espera_resultado_no_resta_aforo(clase_con_hueco, deportista_padre):
    Reserva.objects.create(clase=clase_con_hueco, deportista=deportista_padre, estado='ESPERA')
    assert clase_con_hueco.plazas_disponibles() == 2
