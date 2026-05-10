import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from usuarios.models import Deportista
from django.utils import timezone

@pytest.fixture
def admin_client(db):
    admin = Deportista.objects.create_superuser(username="admin_test", email="admin@test.com", password="password")
    client = APIClient()
    client.force_authenticate(user=admin)
    return client

@pytest.mark.django_db
class TestGraduationFilters:
    """
    Verifica que la data de graduación sea consistente para el filtrado por mes.
    """

    def test_graduation_date_format_consistency(self, admin_client, deportista_padre):
        # 1. Graduamos al deportista hoy
        url = reverse('deportista-actualizar-graduacion', kwargs={'pk': deportista_padre.id})
        response = admin_client.post(url, {'cinturon': 'Azul', 'grados': 1})
        assert response.status_code == status.HTTP_200_OK
        
        # 2. Obtenemos la lista de activos
        url_list = reverse('deportista-activos-backoffice')
        response_list = admin_client.get(url_list)
        
        # 3. Verificamos que la fecha devuelta permita el filtrado por prefijo YYYY-MM
        deportista_data = next(u for u in response_list.data if u['id'] == deportista_padre.id)
        fecha_grad = deportista_data['fecha_ultima_graduacion']
        
        hoy_prefix = timezone.now().strftime('%Y-%m')
        assert fecha_grad.startswith(hoy_prefix), f"La fecha {fecha_grad} debería empezar por {hoy_prefix}"

    def test_graduation_reset_grados_on_belt_change(self, admin_client, deportista_padre):
        # Primero ponemos grados en blanco
        deportista_padre.cinturon = 'Blanco'
        deportista_padre.grados = 3
        deportista_padre.save()

        url = reverse('deportista-actualizar-graduacion', kwargs={'pk': deportista_padre.id})
        
        # Cambiamos a Azul sin pasar grados (debería resetear a 0)
        response = admin_client.post(url, {'cinturon': 'Azul'})
        assert response.status_code == status.HTTP_200_OK
        
        deportista_padre.refresh_from_db()
        assert deportista_padre.cinturon == 'Azul'
        assert deportista_padre.grados == 0
