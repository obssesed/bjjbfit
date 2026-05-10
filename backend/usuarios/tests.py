import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from usuarios.models import Notificacion

Deportista = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(db):
    return Deportista.objects.create_superuser(username='admin', password='pass', email='a@a.com')

@pytest.fixture
def normal_user(db):
    return Deportista.objects.create_user(username='user1', password='pass', email='u1@a.com')

@pytest.mark.django_db
class TestNotificaciones:
    
    def test_admin_puede_crear_notificacion_global(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        data = {
            "titulo": "Aviso Global",
            "mensaje": "Mañana cerrado",
            "es_global": True
        }
        response = api_client.post('/api/notificaciones/', data)
        assert response.status_code == 201
        assert Notificacion.objects.filter(es_global=True).count() == 1

    def test_usuario_puede_ver_notificaciones_pendientes(self, api_client, admin_user, normal_user):
        # Admin crea una global y una personal
        Notificacion.objects.create(titulo="Global", mensaje="G", es_global=True)
        Notificacion.objects.create(titulo="Personal", mensaje="P", es_global=False, destinatario=normal_user)
        
        api_client.force_authenticate(user=normal_user)
        response = api_client.get('/api/notificaciones/pendientes/')
        
        assert response.status_code == 200
        assert len(response.data) == 2

    def test_marcar_notificacion_como_leida(self, api_client, normal_user):
        notif = Notificacion.objects.create(titulo="P", mensaje="P", es_global=False, destinatario=normal_user)
        
        api_client.force_authenticate(user=normal_user)
        response = api_client.post(f'/api/notificaciones/{notif.id}/leer/')
        
        assert response.status_code == 200
        notif.refresh_from_db()
        assert notif.leida is True
        
        # Ya no debería aparecer en pendientes
        response_pendientes = api_client.get('/api/notificaciones/pendientes/')
        assert len(response_pendientes.data) == 0

    def test_global_leida_por_varios(self, api_client, normal_user, db):
        user2 = Deportista.objects.create_user(username='user2', password='pass')
        notif = Notificacion.objects.create(titulo="Global", mensaje="G", es_global=True)
        
        # User 1 lee
        api_client.force_authenticate(user=normal_user)
        api_client.post(f'/api/notificaciones/{notif.id}/leer/')
        
        # User 2 lee
        api_client.force_authenticate(user=user2)
        api_client.post(f'/api/notificaciones/{notif.id}/leer/')
        
        assert notif.leida_por.count() == 2

    def test_admin_no_recibe_notificaciones_globales(self, api_client, admin_user):
        Notificacion.objects.create(titulo="Global", mensaje="G", es_global=True)
        
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/notificaciones/pendientes/')
        
        assert response.status_code == 200
        assert len(response.data) == 0 # El admin no debe ver globales en pendientes
