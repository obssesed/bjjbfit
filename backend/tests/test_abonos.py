import pytest
from rest_framework.test import APIClient
from usuarios.models import Deportista

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestAbonos:
    def test_si_admin_actualiza_metodo_pago_resultado_persiste(self, api_client, admin_user):
        # Creamos un deportista
        deportista = Deportista.objects.create_user(
            username='testatleta',
            email='test@atleta.com',
            password='password123',
            first_name='Test',
            last_name='Atleta',
            nif='12345678Z',
            sexo='M',
            fecha_nacimiento='1990-01-01'
        )
        
        api_client.force_authenticate(user=admin_user)
        
        # Cambiar a CUENTA
        res = api_client.patch(f'/api/deportistas/{deportista.id}/', {
            'metodo_pago': 'CUENTA',
            'cuenta_bancaria': 'ES2112345678901234567890'
        })
        
        assert res.status_code == 200
        deportista.refresh_from_db()
        assert deportista.metodo_pago == 'CUENTA'
        assert deportista.cuenta_bancaria == 'ES2112345678901234567890'

    def test_si_deportista_no_admin_intenta_cambiar_metodo_resultado_200(self, api_client):
        # El propio usuario puede editar su perfil por defecto en DRF ModelViewSet
        deportista = Deportista.objects.create_user(
            username='user1', email='u1@test.com', password='p1',
            first_name='U', last_name='1', nif='1', sexo='M', fecha_nacimiento='1990-01-01'
        )
        api_client.force_authenticate(user=deportista)
        
        res = api_client.patch(f'/api/deportistas/{deportista.id}/', {'metodo_pago': 'CUENTA'})
        assert res.status_code == 200
