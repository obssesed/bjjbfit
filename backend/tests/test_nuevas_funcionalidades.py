import pytest
from rest_framework.test import APIClient
from usuarios.models import Deportista
from django.utils import timezone

@pytest.fixture
def auth_client():
    return APIClient()

@pytest.mark.django_db
class TestNuevasFuncionalidades:

    def test_actualizar_id_interno_exito(self, auth_client):
        """Verifica que un admin puede actualizar el Nº de Socio."""
        admin = Deportista.objects.create_superuser(
            username="admin_socio", password="123", email="admin@socio.com"
        )
        deportista = Deportista.objects.create_user(
            username="alumno_socio", password="123", email="alumno@socio.com"
        )
        auth_client.force_authenticate(user=admin)

        response = auth_client.post(f'/api/deportistas/{deportista.id}/actualizar_id_interno/', {
            'id_interno': 'BJJ-2024-001'
        })
        
        assert response.status_code == 200
        deportista.refresh_from_db()
        assert deportista.id_interno == 'BJJ-2024-001'

    def test_actualizar_graduacion_resetea_grados_al_cambiar_color(self, auth_client):
        """Verifica la lógica de negocio: cambio de cinturón implica grados = 0."""
        admin = Deportista.objects.create_superuser(
            username="admin_belt", password="123", email="admin@belt.com"
        )
        # Deportista Azul con 3 grados
        deportista = Deportista.objects.create_user(
            username="alumno_belt", password="123", email="alumno@belt.com",
            cinturon="Azul", grados=3
        )
        auth_client.force_authenticate(user=admin)

        # Graduamos a Morado
        response = auth_client.post(f'/api/deportistas/{deportista.id}/actualizar_graduacion/', {
            'cinturon': 'Morado',
            'grados': 1 # Intentamos poner 1 grado, pero el backend debería manejar la lógica
        })
        
        assert response.status_code == 200
        deportista.refresh_from_db()
        assert deportista.cinturon == 'Morado'
        assert deportista.grados == 0  # CRÍTICO: Se ha reseteado a 0 en el viewset

    def test_registro_publico_falla_sin_campos_obligatorios(self, auth_client):
        """Verifica que el registro falla si faltan los nuevos campos obligatorios."""
        payload = {
            "username": "test_fail",
            "email": "fail@test.com",
            "password": "password123",
            "first_name": "Incompleto"
            # Faltan last_name, nif, sexo, fecha_nacimiento
        }
        
        response = auth_client.post('/api/deportistas/', payload)
        assert response.status_code == 400
        errors = response.json()
        assert 'nif' in errors
        assert 'fecha_nacimiento' in errors
        assert 'sexo' in errors

    def test_registro_publico_exito_con_todos_los_campos(self, auth_client):
        """Verifica que el registro funciona cuando se envían todos los datos requeridos."""
        payload = {
            "username": "test_ok",
            "email": "ok@test.com",
            "password": "password123",
            "first_name": "Victor",
            "last_name": "Test",
            "nif": "12345678Z",
            "sexo": "M",
            "fecha_nacimiento": "1990-01-01",
            "telefono": "600111222"
        }
        
        response = auth_client.post('/api/deportistas/', payload)
        assert response.status_code == 201
        
        user = Deportista.objects.get(username="test_ok")
        assert user.nif == "12345678Z"
        assert user.sexo == "M"
        assert str(user.fecha_nacimiento) == "1990-01-01"


@pytest.mark.django_db
class TestReporteBackoffice:
    """Tests para validar que la API devuelve todos los campos necesarios para el reporte CSV."""

    def test_api_activos_devuelve_campos_reporte(self, auth_client):
        """Verifica que el endpoint de activos devuelve todos los campos necesarios para exportar."""
        admin = Deportista.objects.create_superuser(
            username="admin_report", password="123", email="admin@report.com"
        )
        deportista = Deportista.objects.create_user(
            username="alumno_report", password="123", email="alumno@report.com",
            first_name="Ana", last_name="López", nif="87654321X",
            sexo="F", fecha_nacimiento="1995-06-15", telefono="611222333",
            plan_activo=True, tipo_plan="ADULTO", cinturon="Azul", grados=2
        )
        deportista.id_interno = "BJJ-001"
        deportista.save()

        auth_client.force_authenticate(user=admin)
        response = auth_client.get('/api/deportistas/activos_backoffice/')
        assert response.status_code == 200

        data = response.json()
        # Buscar nuestro deportista de prueba
        alumno = next((u for u in data if u['username'] == 'alumno_report'), None)
        assert alumno is not None

        # Verificar TODOS los campos que el reporte CSV necesita
        campos_reporte = [
            'first_name', 'last_name', 'nif', 'id_interno', 'email', 'telefono',
            'sexo', 'fecha_nacimiento', 'cinturon', 'grados',
            'tipo_plan', 'es_familiar', 'date_joined', 'hijos_a_cargo'
        ]
        for campo in campos_reporte:
            assert campo in alumno, f"Campo '{campo}' falta en la respuesta de la API"

        # Verificar valores concretos
        assert alumno['first_name'] == "Ana"
        assert alumno['last_name'] == "López"
        assert alumno['nif'] == "87654321X"
        assert alumno['id_interno'] == "BJJ-001"
        assert alumno['sexo'] == "F"
        assert alumno['cinturon'] == "Azul"
        assert alumno['grados'] == 2
        assert alumno['tipo_plan'] == "ADULTO"

    def test_api_filtra_correctamente_por_estado(self, auth_client):
        """Verifica que un deportista activo NO aparece en pendientes ni inactivos (integridad del reporte)."""
        admin = Deportista.objects.create_superuser(
            username="admin_filtro", password="123", email="admin@filtro.com"
        )
        Deportista.objects.create_user(
            username="activo_solo", password="123", email="activo@test.com",
            plan_activo=True, tipo_plan="JUVENIL", first_name="Carlos"
        )

        auth_client.force_authenticate(user=admin)

        # Debe estar en activos
        res_activos = auth_client.get('/api/deportistas/activos_backoffice/')
        nombres_activos = [u['first_name'] for u in res_activos.json()]
        assert "Carlos" in nombres_activos

        # NO debe estar en pendientes
        res_pendientes = auth_client.get('/api/deportistas/pendientes_backoffice/')
        nombres_pendientes = [u['first_name'] for u in res_pendientes.json()]
        assert "Carlos" not in nombres_pendientes

        # NO debe estar en inactivos
        res_inactivos = auth_client.get('/api/deportistas/inactivos_backoffice/')
        nombres_inactivos = [u['first_name'] for u in res_inactivos.json()]
        assert "Carlos" not in nombres_inactivos

    def test_id_interno_se_incluye_en_respuesta_api(self, auth_client):
        """Verifica que el campo id_interno se serializa correctamente tras añadirlo al serializer."""
        admin = Deportista.objects.create_superuser(
            username="admin_id", password="123", email="admin@id.com"
        )
        deportista = Deportista.objects.create_user(
            username="alumno_id", password="123", email="alumno@id.com",
            plan_activo=True
        )

        auth_client.force_authenticate(user=admin)

        # Asignar Nº Socio
        auth_client.post(f'/api/deportistas/{deportista.id}/actualizar_id_interno/', {
            'id_interno': 'SOC-2026-042'
        })

        # Verificar que aparece en el listado
        response = auth_client.get('/api/deportistas/activos_backoffice/')
        alumno = next((u for u in response.json() if u['username'] == 'alumno_id'), None)
        assert alumno is not None
        assert alumno['id_interno'] == 'SOC-2026-042'
