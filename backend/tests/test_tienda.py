import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from reservas.models import Producto

@pytest.mark.django_db
class TestTienda:
    
    def test_listar_productos_publico(self, client, producto_base):
        """Usuarios no autenticados pueden ver productos."""
        url = reverse('producto-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_admin_puede_crear_producto(self, admin_client):
        """Un administrador puede añadir un nuevo producto."""
        url = reverse('producto-list')
        data = {
            "nombre": "Nuevo Kimono",
            "descripcion": "Descripción test",
            "tallas": "A1, A2",
            "estado_stock": "IN_STOCK",
            "orden": 10
        }
        response = admin_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Producto.objects.filter(nombre="Nuevo Kimono").exists()

    def test_usuario_no_puede_crear_producto(self, user_client):
        """Un alumno normal no puede añadir productos."""
        url = reverse('producto-list')
        data = {"nombre": "Hack"}
        response = user_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_puede_editar_producto(self, admin_client, producto_base):
        """Un administrador puede modificar un producto existente."""
        url = reverse('producto-detail', args=[producto_base.id])
        data = {"nombre": "Kimono Editado", "estado_stock": "OUT_OF_STOCK"}
        response = admin_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        producto_base.refresh_from_db()
        assert producto_base.nombre == "Kimono Editado"
        assert producto_base.estado_stock == "OUT_OF_STOCK"

    def test_admin_puede_eliminar_producto(self, admin_client, producto_base):
        """Un administrador puede borrar un producto."""
        url = reverse('producto-detail', args=[producto_base.id])
        response = admin_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Producto.objects.filter(id=producto_base.id).exists()

@pytest.fixture
def producto_base(db):
    return Producto.objects.create(
        nombre="Kimono Base",
        descripcion="Test",
        tallas="A1",
        estado_stock="IN_STOCK"
    )

@pytest.fixture
def user_client(db):
    from usuarios.models import Deportista
    client = APIClient()
    user = Deportista.objects.create_user(username='alumno', password='password123')
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def admin_client(db):
    from usuarios.models import Deportista
    client = APIClient()
    admin = Deportista.objects.create_superuser(username='admin', password='password123', email='admin@test.com')
    client.force_authenticate(user=admin)
    return client
