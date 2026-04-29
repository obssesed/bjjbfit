import pytest
from rest_framework.test import APIClient
from usuarios.models import Deportista
from reservas.models import ClaseBJJ, Reserva
from django.utils import timezone

@pytest.fixture
def auth_client():
    return APIClient()

@pytest.mark.django_db
class TestUsuariosViews:
    def test_activos_backoffice_rechaza_no_staff(self, auth_client):
        usuario_comun = Deportista.objects.create_user(
            username="user1", email="a@a.com", password="123"
        )
        auth_client.force_authenticate(user=usuario_comun)
        response = auth_client.get('/api/deportistas/activos_backoffice/')
        assert response.status_code == 403

    def test_activos_backoffice_permite_staff_y_filtra_activos(self, auth_client):
        # Crear staff
        staff = Deportista.objects.create_superuser(
            username="admin_test", password="123", email="ad@ad.com", plan_activo=True
        )
        # Crear usuario comun activo
        Deportista.objects.create_user(
            username="user_activo", password="123", email="b@b.com", plan_activo=True, first_name="Ana"
        )
        # Crear usuario inactivo que ya tuvo plan (baja)
        user_baja = Deportista.objects.create_user(
            username="user_baja", password="123", email="c@c.com", plan_activo=False, 
            first_name="Zac", tipo_plan="ADULTO"
        )

        # Crear usuario pendiente SIN historial de reservas y SIN plan (alta nueva)
        Deportista.objects.create_user(
            username="user_pendiente", password="123", email="d@d.com", plan_activo=False, first_name="Nuevo"
        )

        auth_client.force_authenticate(user=staff)

        # --- Activos ---
        response = auth_client.get('/api/deportistas/activos_backoffice/')
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Staff plan_activo + user_activo
        nombres = [u.get('first_name', '') for u in data]
        assert nombres[0] == ""
        assert nombres[1] == "Ana"

        # --- Inactivos (con historial) ---
        response_inactivos = auth_client.get('/api/deportistas/inactivos_backoffice/')
        assert response_inactivos.status_code == 200
        data_inactivos = response_inactivos.json()
        assert len(data_inactivos) == 1
        assert data_inactivos[0]['username'] == "user_baja"

        # --- Pendientes (sin historial) ---
        response_pendientes = auth_client.get('/api/deportistas/pendientes_backoffice/')
        assert response_pendientes.status_code == 200
        data_pendientes = response_pendientes.json()
        assert len(data_pendientes) == 1
        assert data_pendientes[0]['username'] == "user_pendiente"

    def test_activar_plan(self, auth_client):
        """Verifica que el admin puede activar un plan para un deportista."""
        staff = Deportista.objects.create_superuser(
            username="admin_plan", password="123", email="plan@ad.com"
        )
        deportista = Deportista.objects.create_user(
            username="nuevo_alumno", password="123", email="nuevo@test.com", plan_activo=False
        )
        auth_client.force_authenticate(user=staff)

        # Activar plan mensual adulto
        response = auth_client.post(f'/api/deportistas/{deportista.id}/activar_plan/', {'tipo_plan': 'ADULTO'})
        assert response.status_code == 200

        deportista.refresh_from_db()
        assert deportista.plan_activo is True
        assert deportista.tipo_plan == 'ADULTO'
        assert deportista.es_familiar is False

    def test_activar_plan_familiar(self, auth_client):
        """Verifica que se puede activar un plan con flag familiar."""
        staff = Deportista.objects.create_superuser(
            username="admin_fam", password="123", email="fam@ad.com"
        )
        deportista = Deportista.objects.create_user(
            username="alumno_fam", password="123", email="fam@test.com", plan_activo=False
        )
        auth_client.force_authenticate(user=staff)

        response = auth_client.post(f'/api/deportistas/{deportista.id}/activar_plan/', {
            'tipo_plan': 'JUVENIL',
            'es_familiar': True
        })
        assert response.status_code == 200

        deportista.refresh_from_db()
        assert deportista.plan_activo is True
        assert deportista.tipo_plan == 'JUVENIL'
        assert deportista.es_familiar is True

    def test_activar_plan_rechaza_tipo_invalido(self, auth_client):
        """Verifica que no se puede activar un plan con tipo inválido."""
        staff = Deportista.objects.create_superuser(
            username="admin_inv", password="123", email="inv@ad.com"
        )
        deportista = Deportista.objects.create_user(
            username="alumno_inv", password="123", email="inv@test.com", plan_activo=False
        )
        auth_client.force_authenticate(user=staff)

        response = auth_client.post(f'/api/deportistas/{deportista.id}/activar_plan/', {'tipo_plan': 'INEXISTENTE'})
        assert response.status_code == 400

