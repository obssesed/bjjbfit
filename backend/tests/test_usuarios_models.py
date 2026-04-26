import pytest
from usuarios.models import Deportista

@pytest.mark.django_db
def test_si_creacion_deportista_resultado_padre_tutor_asignado(deportista_padre, deportista_hijo):
    assert deportista_hijo.padre_tutor == deportista_padre
    assert deportista_hijo in deportista_padre.hijos_a_cargo.all()

@pytest.mark.django_db
def test_si_obtener_string_resultado_formato_correcto(deportista_padre):
    deportista_padre.cinturon = "Negro 1 Grado"
    deportista_padre.save()
    assert str(deportista_padre) == "padre1 - Negro 1 Grado"

@pytest.mark.django_db
def test_si_string_vacio_resultado_cinturon_blanco():
    d = Deportista.objects.create(username="novato")
    assert str(d) == "novato - Cinturón blanco sin grados"

@pytest.mark.django_db
def test_si_deportista_sube_de_grado_resultado_fecha_actualiza(deportista_padre):
    from django.utils import timezone
    assert deportista_padre.fecha_ultima_graduacion == timezone.now().date()
    
    # Simulamos que pasa 1 dia y se gradua
    dia_pasado = timezone.now().date() - timezone.timedelta(days=1)
    deportista_padre.fecha_ultima_graduacion = dia_pasado
    deportista_padre.save()
    
    deportista_padre.grados = 1
    deportista_padre.save()
    
    assert deportista_padre.fecha_ultima_graduacion == timezone.now().date()
