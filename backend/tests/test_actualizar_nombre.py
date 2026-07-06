"""Tests para el endpoint actualizar_nombre (Edición de nombre desde el backoffice)."""
import pytest
from rest_framework.test import APIClient
from usuarios.models import Deportista


@pytest.fixture
def auth_client():
    return APIClient()


@pytest.mark.django_db
class TestActualizarNombre:
    """Batería de tests para el endpoint POST /api/deportistas/{id}/actualizar_nombre/"""

    def test_admin_actualiza_nombre_correctamente(self, auth_client):
        """Caso OK: El admin corrige nombre y apellidos de un deportista."""
        staff = Deportista.objects.create_superuser(
            username="admin_nom", password="123", email="nom_admin@ad.com"
        )
        deportista = Deportista.objects.create_user(
            username="alumno_nombre", password="123", email="nombre@test.com",
            first_name="Hogo", last_name="nicolas Gonzales"
        )
        auth_client.force_authenticate(user=staff)

        response = auth_client.post(
            f'/api/deportistas/{deportista.id}/actualizar_nombre/',
            {'first_name': 'Hugo', 'last_name': 'Nicolás González'}
        )
        assert response.status_code == 200
        assert 'success' in response.json()

        deportista.refresh_from_db()
        assert deportista.first_name == 'Hugo'
        assert deportista.last_name == 'Nicolás González'

    def test_admin_actualiza_solo_nombre(self, auth_client):
        """Caso OK: El admin actualiza solo el nombre, dejando apellido vacío."""
        staff = Deportista.objects.create_superuser(
            username="admin_nom2", password="123", email="nom2@ad.com"
        )
        deportista = Deportista.objects.create_user(
            username="alumno_solo_nom", password="123", email="solonom@test.com",
            first_name="Pedro", last_name="García"
        )
        auth_client.force_authenticate(user=staff)

        response = auth_client.post(
            f'/api/deportistas/{deportista.id}/actualizar_nombre/',
            {'first_name': 'Pablo', 'last_name': ''}
        )
        assert response.status_code == 200

        deportista.refresh_from_db()
        assert deportista.first_name == 'Pablo'
        assert deportista.last_name == ''

    def test_admin_actualiza_solo_apellido(self, auth_client):
        """Caso OK: El admin actualiza solo el apellido, dejando nombre vacío."""
        staff = Deportista.objects.create_superuser(
            username="admin_nom3", password="123", email="nom3@ad.com"
        )
        deportista = Deportista.objects.create_user(
            username="alumno_solo_ape", password="123", email="soloape@test.com",
            first_name="Ana", last_name="López"
        )
        auth_client.force_authenticate(user=staff)

        response = auth_client.post(
            f'/api/deportistas/{deportista.id}/actualizar_nombre/',
            {'first_name': '', 'last_name': 'López Martínez'}
        )
        assert response.status_code == 200

        deportista.refresh_from_db()
        assert deportista.first_name == ''
        assert deportista.last_name == 'López Martínez'

    def test_nombre_y_apellido_vacios_retorna_error(self, auth_client):
        """Caso KO: No se permite guardar nombre y apellido ambos vacíos."""
        staff = Deportista.objects.create_superuser(
            username="admin_nom4", password="123", email="nom4@ad.com"
        )
        deportista = Deportista.objects.create_user(
            username="alumno_vacio_nom", password="123", email="vacnom@test.com",
            first_name="Marta", last_name="Soto"
        )
        auth_client.force_authenticate(user=staff)

        response = auth_client.post(
            f'/api/deportistas/{deportista.id}/actualizar_nombre/',
            {'first_name': '', 'last_name': ''}
        )
        assert response.status_code == 400
        assert 'error' in response.json()

        # Verificar que no cambió
        deportista.refresh_from_db()
        assert deportista.first_name == 'Marta'
        assert deportista.last_name == 'Soto'

    def test_nombre_solo_espacios_retorna_error(self, auth_client):
        """Caso KO: Nombre y apellido con solo espacios son rechazados (se hace strip)."""
        staff = Deportista.objects.create_superuser(
            username="admin_nom5", password="123", email="nom5@ad.com"
        )
        deportista = Deportista.objects.create_user(
            username="alumno_spaces_nom", password="123", email="spacesnom@test.com",
            first_name="Carlos", last_name="Ruiz"
        )
        auth_client.force_authenticate(user=staff)

        response = auth_client.post(
            f'/api/deportistas/{deportista.id}/actualizar_nombre/',
            {'first_name': '   ', 'last_name': '   '}
        )
        assert response.status_code == 400

    def test_usuario_no_admin_no_puede_actualizar_nombre(self, auth_client):
        """Caso KO: Un usuario no admin no puede actualizar el nombre de otro usuario."""
        usuario_comun = Deportista.objects.create_user(
            username="user_no_admin_nom", password="123", email="nonadmin_nom@test.com",
            plan_activo=True
        )
        otro = Deportista.objects.create_user(
            username="otro_user_nom", password="123", email="otro_nom@test.com",
            first_name="David"
        )
        auth_client.force_authenticate(user=usuario_comun)

        response = auth_client.post(
            f'/api/deportistas/{otro.id}/actualizar_nombre/',
            {'first_name': 'Hackeado', 'last_name': 'Malicioso'}
        )
        # 404: El queryset no expone deportistas ajenos a usuarios no-staff
        assert response.status_code in (403, 404)

        # Verificar que el nombre no cambió
        otro.refresh_from_db()
        assert otro.first_name == 'David'

    def test_nombre_se_trimmea_correctamente(self, auth_client):
        """Caso OK: Espacios al inicio/final del nombre se eliminan automáticamente."""
        staff = Deportista.objects.create_superuser(
            username="admin_nom6", password="123", email="nom6@ad.com"
        )
        deportista = Deportista.objects.create_user(
            username="alumno_trim_nom", password="123", email="trimnom@test.com",
            first_name="Juan"
        )
        auth_client.force_authenticate(user=staff)

        response = auth_client.post(
            f'/api/deportistas/{deportista.id}/actualizar_nombre/',
            {'first_name': '  Juan Carlos  ', 'last_name': '  Pérez  '}
        )
        assert response.status_code == 200

        deportista.refresh_from_db()
        assert deportista.first_name == 'Juan Carlos'
        assert deportista.last_name == 'Pérez'
