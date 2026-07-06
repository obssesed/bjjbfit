"""Tests para el endpoint crear_alta_manual (Añadir altas manualmente desde el backoffice)."""
import pytest
from rest_framework.test import APIClient
from usuarios.models import Deportista, Plan

@pytest.fixture
def auth_client():
    return APIClient()

@pytest.mark.django_db
class TestAltasManuales:
    """Batería de tests para el endpoint POST /api/deportistas/crear_alta_manual/"""

    def test_admin_crea_alta_manual_correctamente(self, auth_client):
        """Caso OK: El admin crea un nuevo usuario con plan activo."""
        staff = Deportista.objects.create_superuser(
            username="admin_altas", password="123", email="admin_altas@ad.com"
        )
        plan = Plan.objects.create(nombre="Plan Mensual Test", precio_base=50.0)
        auth_client.force_authenticate(user=staff)

        datos = {
            "first_name": "Juan",
            "last_name": "Pérez",
            "email": "juan.perez.test@bjjbfit.com",
            "nif": "12345678A",
            "sexo": "M",
            "fecha_nacimiento": "1990-01-01",
            "cinturon": "Blanco",
            "telefono": "600100200",
            "plan_activo": True,
            "tipo_plan": plan.id,
            "es_familiar": False
        }

        response = auth_client.post('/api/deportistas/crear_alta_manual/', datos, format='json')
        assert response.status_code == 201
        assert 'success' in response.json()
        assert response.json()['usuario']['first_name'] == "Juan"

        # Verificar BD
        nuevo_user = Deportista.objects.get(email="juan.perez.test@bjjbfit.com")
        assert nuevo_user.requiere_cambio_password == True
        assert nuevo_user.plan_activo == True
        assert nuevo_user.tipo_plan == plan
        # Validar que se asignó la contraseña y funciona (Bjjbfit2026!)
        assert nuevo_user.check_password("Bjjbfit2026!")

    def test_usuario_no_admin_no_puede_crear_alta(self, auth_client):
        """Caso KO: Usuario normal no tiene acceso a crear alta manual."""
        usuario_comun = Deportista.objects.create_user(
            username="user_normal", password="123", email="normal@test.com"
        )
        auth_client.force_authenticate(user=usuario_comun)

        response = auth_client.post('/api/deportistas/crear_alta_manual/', {"first_name": "Hack"}, format='json')
        assert response.status_code in (403, 404)

    def test_crear_alta_manual_valida_campos_requeridos(self, auth_client):
        """Caso KO: Si faltan campos requeridos (email), devuelve 400."""
        staff = Deportista.objects.create_superuser(
            username="admin_altas_ko", password="123", email="admin_altas_ko@ad.com"
        )
        auth_client.force_authenticate(user=staff)

        # Falta el email, que es required y unique
        datos = {
            "first_name": "Incompleto",
            "last_name": "Pérez"
        }

        response = auth_client.post('/api/deportistas/crear_alta_manual/', datos, format='json')
        assert response.status_code == 400
        assert 'email' in response.json()
