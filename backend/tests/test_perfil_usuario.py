import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from usuarios.models import Deportista

@pytest.fixture
def auth_client(db, deportista_padre):
    client = APIClient()
    client.force_authenticate(user=deportista_padre)
    return client

@pytest.mark.django_db
class TestPerfilUsuario:
    """
    Tests para la gestión del perfil de usuario (endpoint /me).
    """

    def test_ver_mi_perfil(self, auth_client, deportista_padre):
        url = reverse('deportista-me')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == deportista_padre.username
        assert response.data['email'] == deportista_padre.email

    def test_actualizar_datos_permitidos(self, auth_client, deportista_padre):
        url = reverse('deportista-me')
        data = {
            'email': 'nuevo@correo.com',
            'telefono': '666777888',
            'nif': '12345678Z'
        }
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        deportista_padre.refresh_from_db()
        assert deportista_padre.email == 'nuevo@correo.com'
        assert deportista_padre.telefono == '666777888'
        assert deportista_padre.nif == '12345678Z'

    def test_intentar_actualizar_datos_prohibidos(self, auth_client, deportista_padre):
        url = reverse('deportista-me')
        original_first_name = deportista_padre.first_name
        original_cinturon = deportista_padre.cinturon
        
        data = {
            'first_name': 'Hacker',
            'cinturon': 'Negro',
            'grados': 4,
            'plan_activo': True
        }
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        deportista_padre.refresh_from_db()
        # No deberían haber cambiado
        assert deportista_padre.first_name == original_first_name
        assert deportista_padre.cinturon == original_cinturon
        # El plan_activo se mantiene en True porque deportista_padre ya era True en conftest
        assert deportista_padre.plan_activo == True 

    def test_validacion_cuenta_bancaria_obligatoria(self, auth_client, deportista_padre):
        url = reverse('deportista-me')
        
        # Intentar poner CUENTA sin poner cuenta_bancaria
        data = {
            'metodo_pago': 'CUENTA',
            'cuenta_bancaria': ''
        }
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'cuenta_bancaria' in response.data

    def test_actualizacion_exitosa_con_cuenta(self, auth_client, deportista_padre):
        url = reverse('deportista-me')
        
        data = {
            'metodo_pago': 'CUENTA',
            'cuenta_bancaria': 'ES991234567890'
        }
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        deportista_padre.refresh_from_db()
        assert deportista_padre.metodo_pago == 'CUENTA'
        assert deportista_padre.cuenta_bancaria == 'ES991234567890'

    def test_ver_perfil_con_hijos_menores(self, auth_client, deportista_padre, deportista_hijo):
        from datetime import date
        # deportista_hijo necesita fecha para ser detectado como < 14
        deportista_hijo.fecha_nacimiento = date(2020, 1, 1)
        deportista_hijo.save()

        url = reverse('deportista-me')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Verificamos que el hijo aparece en la lista de hijos_a_cargo
        hijos = response.data['hijos_a_cargo']
        assert len(hijos) >= 1
        assert any(h['id'] == deportista_hijo.id for h in hijos)

    def test_no_ver_hijos_mayores_de_14(self, auth_client, deportista_padre, deportista_hijo):
        from datetime import date, timedelta
        # Ponemos al hijo con 15 años
        deportista_hijo.fecha_nacimiento = date.today() - timedelta(days=365*15)
        deportista_hijo.save()

        url = reverse('deportista-me')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        hijos = response.data['hijos_a_cargo']
        assert all(h['id'] != deportista_hijo.id for h in hijos)

    def test_actualizar_perfil_hijo_exitoso(self, auth_client, deportista_padre, deportista_hijo):
        url = reverse('deportista-actualizar-perfil-hijo', kwargs={'pk': deportista_hijo.id})
        data = {'email': 'hijo_nuevo@test.com', 'telefono': '999888777'}
        
        response = auth_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        deportista_hijo.refresh_from_db()
        assert deportista_hijo.email == 'hijo_nuevo@test.com'
        assert deportista_hijo.telefono == '999888777'

    def test_actualizar_perfil_hijo_ajeno_prohibido(self, auth_client, deportista_hijo):
        # Creamos otro padre que NO es el tutor
        otro_padre = Deportista.objects.create_user(username="otro", email="o@o.com", password="123")
        client_ajeno = APIClient()
        client_ajeno.force_authenticate(user=otro_padre)

        url = reverse('deportista-actualizar-perfil-hijo', kwargs={'pk': deportista_hijo.id})
        response = client_ajeno.patch(url, {'email': 'hack@test.com'})
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_crear_perfil_hijo_exitoso(self, auth_client, deportista_padre):
        from datetime import date
        hoy = date.today()
        nacimiento = date(hoy.year - 10, hoy.month, hoy.day).strftime('%Y-%m-%d')
        
        url = '/api/deportistas/crear_perfil_hijo/'
        payload = {
            "first_name": "Nuevo",
            "last_name": "Hijo",
            "fecha_nacimiento": nacimiento,
            "sexo": "M"
        }
        
        response = auth_client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED, response.json()
        
        # Verificar en base de datos
        hijos_db = Deportista.objects.filter(padre_tutor=deportista_padre)
        assert hijos_db.count() >= 1
        nuevo_hijo = hijos_db.get(first_name="Nuevo")
        assert nuevo_hijo.nif == deportista_padre.nif

    def test_crear_perfil_hijo_mayor_de_14_falla(self, auth_client, deportista_padre):
        from datetime import date
        hoy = date.today()
        nacimiento = date(hoy.year - 15, hoy.month, hoy.day).strftime('%Y-%m-%d')
        
        url = '/api/deportistas/crear_perfil_hijo/'
        payload = {
            "first_name": "Hijo",
            "last_name": "Mayor",
            "fecha_nacimiento": nacimiento,
            "sexo": "M"
        }
        
        response = auth_client.post(url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "menores de 14 años" in response.json()['error']
