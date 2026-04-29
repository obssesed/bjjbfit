import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from reservas.models import PlantillaClase, ClaseBJJ, Reserva
from usuarios.models import Plan, Deportista

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def plan_adulto(db):
    return Plan.objects.create(
        nombre="Plan Adulto Test",
        precio_base=70.0,
        categoria_edad='ADULTO',
        activo=True
    )

@pytest.fixture
def plan_infantil(db):
    return Plan.objects.create(
        nombre="Plan Infantil Test",
        precio_base=40.0,
        categoria_edad='INFANTIL',
        activo=True
    )

@pytest.mark.django_db
class TestReglasNegocioV2:
    
    def test_propagacion_mantiene_icono_y_categoria(self, api_client):
        # 1. Creamos la plantilla
        plantilla = PlantillaClase.objects.create(
            titulo="Clase Propagada",
            icono="🥋",
            hora_inicio="10:00:00",
            duracion_minutos=60,
            capacidad_maxima=20,
            categoria_acceso='INFANTIL'
        )
        
        # 2. Disparamos la propagación vía API (Admin requerido, pero aquí simulamos)
        # O podemos llamar directamente a la lógica de la vista si queremos test unitario puro
        # Por brevedad y para probar la lógica de negocio, llamaremos al endpoint
        # Pero necesitamos un usuario admin
        admin = Deportista.objects.create_superuser(username='admin_test', email='a@t.com', password='p')
        api_client.force_authenticate(user=admin)
        
        # Hoy y mañana para asegurar rango
        hoy = timezone.now().date()
        mañana = hoy + timezone.timedelta(days=1)
        payload = {
            'fecha_inicio': hoy.isoformat(),
            'fecha_fin': mañana.isoformat(),
            'dias_semana': [hoy.weekday(), mañana.weekday()]
        }
        
        res = api_client.post(f'/api/programacion/{plantilla.id}/propagar/', payload, format='json')
        assert res.status_code == 200
        print(f"Respuesta API: {res.data}")
        
        # 3. Verificamos que se crearon clases (deberían ser 2)
        clases = ClaseBJJ.objects.filter(titulo="Clase Propagada")
        assert clases.count() >= 1, f"No se crearon clases. Respuesta: {res.data}"
        
        clase = clases.first()
        assert clase.icono == "🥋"
        assert clase.categoria_acceso == 'INFANTIL'
        assert clase.capacidad_maxima == 20

    def test_validacion_categoria_plan_impide_reserva_incorrecta(self, api_client, plan_adulto, plan_infantil):
        # 1. Creamos una clase de ADULTOS
        inicio = timezone.now() + timezone.timedelta(days=1)
        clase_adultos = ClaseBJJ.objects.create(
            titulo="BJJ Adultos",
            fecha_hora_inicio=inicio,
            categoria_acceso='ADULTO',
            capacidad_maxima=10
        )
        
        # 2. Creamos un deportista con plan INFANTIL
        niño = Deportista.objects.create_user(
            username="niño_test",
            email="niño@test.com",
            password="pass",
            plan_activo=True,
            tipo_plan=plan_infantil
        )
        
        # 3. Intentamos reservar clase de adultos con plan infantil
        api_client.force_authenticate(user=niño)
        res = api_client.post('/api/reservas/', {'clase': clase_adultos.id})
        
        assert res.status_code == 400
        assert "Esta clase es para la categoría Solo Adultos" in str(res.data)

    def test_validacion_categoria_plan_permite_reserva_correcta(self, api_client, plan_adulto):
        # 1. Clase Adultos
        inicio = timezone.now() + timezone.timedelta(days=1)
        clase_adultos = ClaseBJJ.objects.create(
            titulo="BJJ Adultos OK",
            fecha_hora_inicio=inicio,
            categoria_acceso='ADULTO',
            capacidad_maxima=10
        )
        
        # 2. Adulto con plan Adulto
        adulto = Deportista.objects.create_user(
            username="adulto_ok",
            email="adulto@test.com",
            password="pass",
            plan_activo=True,
            tipo_plan=plan_adulto
        )
        
        api_client.force_authenticate(user=adulto)
        res = api_client.post('/api/reservas/', {'clase': clase_adultos.id})
        
        assert res.status_code == 201
        assert res.data['estado'] == 'CONFIRMADA'
