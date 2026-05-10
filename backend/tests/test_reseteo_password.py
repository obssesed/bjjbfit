import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from usuarios.models import Deportista, SolicitudReseteoPassword
from django.contrib.auth.hashers import check_password

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestReseteoPassword:

    def test_solicitar_reseteo_exito(self, api_client):
        user = Deportista.objects.create_user(username="olvidadizo", password="pwd")
        url = "/api/deportistas/solicitar_reseteo/"
        
        response = api_client.post(url, {"username": "olvidadizo"})
        
        assert response.status_code == status.HTTP_200_OK
        assert SolicitudReseteoPassword.objects.filter(usuario=user).count() == 1
        
    def test_solicitar_reseteo_usuario_no_existe_falso_positivo(self, api_client):
        # Debe devolver 200 para no revelar si el usuario existe o no
        url = "/api/deportistas/solicitar_reseteo/"
        response = api_client.post(url, {"username": "fantasma"})
        
        assert response.status_code == status.HTTP_200_OK
        assert SolicitudReseteoPassword.objects.count() == 0

    def test_admin_puede_aprobar_solicitud(self, api_client):
        admin = Deportista.objects.create_superuser(username="admin", email="admin@test.com", password="pwd")
        user = Deportista.objects.create_user(username="olvidadizo2", email="olvidadizo2@test.com", password="pwd")
        solicitud = SolicitudReseteoPassword.objects.create(usuario=user)
        
        api_client.force_authenticate(user=admin)
        url = f"/api/solicitudes-reseteo/{solicitud.id}/aprobar/"
        
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar que se generó una clave y se actualizó el usuario
        assert 'temp_password' in response.data
        user.refresh_from_db()
        solicitud.refresh_from_db()
        
        assert solicitud.resuelta is True
        assert user.requiere_cambio_password is True
        assert check_password(response.data['temp_password'], user.password)

    def test_usuario_puede_cambiar_password_obligatorio(self, api_client):
        user = Deportista.objects.create_user(username="olvidadizo", password="temp_pwd", requiere_cambio_password=True)
        
        api_client.force_authenticate(user=user)
        url = "/api/deportistas/cambiar_password_obligatorio/"
        
        response = api_client.post(url, {"new_password": "nueva_password_segura"})
        assert response.status_code == status.HTTP_200_OK
        
        user.refresh_from_db()
        assert user.requiere_cambio_password is False
        assert check_password("nueva_password_segura", user.password)

    def test_usuario_no_puede_cambiar_si_no_es_obligatorio(self, api_client):
        user = Deportista.objects.create_user(username="normal", password="pwd", requiere_cambio_password=False)
        
        api_client.force_authenticate(user=user)
        url = "/api/deportistas/cambiar_password_obligatorio/"
        
        response = api_client.post(url, {"new_password": "nueva_password_segura"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No requieres un cambio de contraseña obligatorio" in response.data['error']
