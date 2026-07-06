"""Tests para el endpoint actualizar_nif (Edición de DNI desde el backoffice)."""
import pytest
from rest_framework.test import APIClient
from usuarios.models import Deportista


@pytest.fixture
def auth_client():
    return APIClient()


@pytest.mark.django_db
class TestActualizarNif:
    """Batería de tests para el endpoint POST /api/deportistas/{id}/actualizar_nif/"""

    def test_admin_actualiza_nif_correctamente(self, auth_client):
        """Caso OK: El admin actualiza el DNI/NIF de un deportista sin DNI."""
        staff = Deportista.objects.create_superuser(
            username="admin_nif", password="123", email="nif_admin@ad.com"
        )
        deportista = Deportista.objects.create_user(
            username="alumno_sin_dni", password="123", email="sindni@test.com",
            first_name="Alan", nif=""
        )
        auth_client.force_authenticate(user=staff)

        response = auth_client.post(
            f'/api/deportistas/{deportista.id}/actualizar_nif/',
            {'nif': '12345678Z'}
        )
        assert response.status_code == 200
        assert 'success' in response.json()

        deportista.refresh_from_db()
        assert deportista.nif == '12345678Z'

    def test_admin_cambia_nif_existente(self, auth_client):
        """Caso OK: El admin cambia un DNI/NIF que ya existía por uno nuevo."""
        staff = Deportista.objects.create_superuser(
            username="admin_nif2", password="123", email="nif2@ad.com"
        )
        deportista = Deportista.objects.create_user(
            username="alumno_con_dni", password="123", email="condni@test.com",
            first_name="Pedro", nif="99999999X"
        )
        auth_client.force_authenticate(user=staff)

        response = auth_client.post(
            f'/api/deportistas/{deportista.id}/actualizar_nif/',
            {'nif': '11111111A'}
        )
        assert response.status_code == 200

        deportista.refresh_from_db()
        assert deportista.nif == '11111111A'

    def test_nif_vacio_retorna_error(self, auth_client):
        """Caso KO: No se permite guardar un NIF vacío."""
        staff = Deportista.objects.create_superuser(
            username="admin_nif3", password="123", email="nif3@ad.com"
        )
        deportista = Deportista.objects.create_user(
            username="alumno_vacio", password="123", email="vacio@test.com",
            first_name="Laura", nif="88888888B"
        )
        auth_client.force_authenticate(user=staff)

        response = auth_client.post(
            f'/api/deportistas/{deportista.id}/actualizar_nif/',
            {'nif': ''}
        )
        assert response.status_code == 400
        assert 'error' in response.json()

        # Verificar que no cambió
        deportista.refresh_from_db()
        assert deportista.nif == '88888888B'

    def test_nif_solo_espacios_retorna_error(self, auth_client):
        """Caso KO: Un NIF con solo espacios es rechazado (se hace strip)."""
        staff = Deportista.objects.create_superuser(
            username="admin_nif4", password="123", email="nif4@ad.com"
        )
        deportista = Deportista.objects.create_user(
            username="alumno_spaces", password="123", email="spaces@test.com",
            first_name="Marta"
        )
        auth_client.force_authenticate(user=staff)

        response = auth_client.post(
            f'/api/deportistas/{deportista.id}/actualizar_nif/',
            {'nif': '   '}
        )
        assert response.status_code == 400

    def test_usuario_no_admin_no_puede_actualizar_nif(self, auth_client):
        """Caso KO: Un usuario no admin no puede acceder al endpoint de otro usuario.
        
        El get_queryset del ViewSet filtra los deportistas visibles, así que un
        usuario no-staff recibe 404 (no encuentra el recurso) en lugar de 403,
        lo cual es equivalente en seguridad y no revela la existencia del recurso.
        """
        usuario_comun = Deportista.objects.create_user(
            username="user_no_admin", password="123", email="nonadmin@test.com",
            plan_activo=True
        )
        otro = Deportista.objects.create_user(
            username="otro_user", password="123", email="otro@test.com"
        )
        auth_client.force_authenticate(user=usuario_comun)

        response = auth_client.post(
            f'/api/deportistas/{otro.id}/actualizar_nif/',
            {'nif': '55555555C'}
        )
        # 404: El queryset no expone deportistas ajenos a usuarios no-staff
        assert response.status_code in (403, 404)

    def test_nif_se_trimmea_correctamente(self, auth_client):
        """Caso OK: Espacios al inicio/final del NIF se eliminan automáticamente."""
        staff = Deportista.objects.create_superuser(
            username="admin_nif5", password="123", email="nif5@ad.com"
        )
        deportista = Deportista.objects.create_user(
            username="alumno_trim", password="123", email="trim@test.com",
            first_name="Carlos"
        )
        auth_client.force_authenticate(user=staff)

        response = auth_client.post(
            f'/api/deportistas/{deportista.id}/actualizar_nif/',
            {'nif': '  44444444D  '}
        )
        assert response.status_code == 200

        deportista.refresh_from_db()
        assert deportista.nif == '44444444D'
