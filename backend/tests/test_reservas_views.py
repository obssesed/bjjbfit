import pytest
from rest_framework.test import APIClient
from reservas.models import Reserva

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestReservasViews:
    def test_si_no_autenticado_resultado_401(self, api_client, clase_con_hueco):
        res = api_client.post('/api/reservas/', {'clase': clase_con_hueco.id})
        assert res.status_code == 401

    def test_si_usuario_sin_plan_hace_reserva_resultado_400_bad_request(self, api_client, clase_con_hueco, deportista_padre_sin_plan):
        api_client.force_authenticate(user=deportista_padre_sin_plan)
        res = api_client.post('/api/reservas/', {'clase': clase_con_hueco.id})
        assert res.status_code == 400
        assert "no tiene un plan activo" in str(res.data)

    def test_si_usuario_cuyo_plan_es_valido_resultado_estado_confirmada(self, api_client, clase_con_hueco, deportista_padre):
        api_client.force_authenticate(user=deportista_padre)
        res = api_client.post('/api/reservas/', {'clase': clase_con_hueco.id})
        print(f"DEBUG DATA: {res.data}")
        assert res.status_code == 201
        assert res.data['estado'] == 'CONFIRMADA'

    def test_si_usuario_reserva_clase_llena_resultado_estado_espera(self, api_client, clase_con_hueco, deportista_padre, deportista_hijo, deportista_padre_sin_plan):
        deportista_padre_sin_plan.plan_activo = True
        deportista_padre_sin_plan.save()
        
        Reserva.objects.create(clase=clase_con_hueco, deportista=deportista_hijo, estado='CONFIRMADA')
        Reserva.objects.create(clase=clase_con_hueco, deportista=deportista_padre_sin_plan, estado='CONFIRMADA')
        
        # Aforo lleno
        assert clase_con_hueco.plazas_disponibles() == 0
        
        api_client.force_authenticate(user=deportista_padre)
        res = api_client.post('/api/reservas/', {'clase': clase_con_hueco.id})
        
        assert res.status_code == 201
        assert res.data['estado'] == 'ESPERA'

    def test_si_usuario_reserva_para_hijo_tutelado_resultado_reserva_a_nombre_del_hijo(self, api_client, clase_con_hueco, deportista_padre, deportista_hijo):
        api_client.force_authenticate(user=deportista_padre)
        res = api_client.post('/api/reservas/', {
            'clase': clase_con_hueco.id,
            'deportista': deportista_hijo.id
        })
        assert res.status_code == 201
        reserva_id = res.data.get('id')
        assert Reserva.objects.get(id=reserva_id).deportista == deportista_hijo

    def test_si_usuario_reserva_para_tercero_no_tutelado_resultado_403_forbidden(self, api_client, clase_con_hueco, deportista_padre, deportista_padre_sin_plan):
        deportista_padre_sin_plan.plan_activo = True
        deportista_padre_sin_plan.save()
        api_client.force_authenticate(user=deportista_padre)
        res = api_client.post('/api/reservas/', {
            'clase': clase_con_hueco.id,
            'deportista': deportista_padre_sin_plan.id
        })
        assert res.status_code == 403

    def test_si_usuario_cancela_reserva_resultado_soft_delete_y_lista_espera_avanza(self, api_client, clase_con_hueco, deportista_padre, deportista_hijo):
        clase_con_hueco.capacidad_maxima = 1
        clase_con_hueco.save()
        
        r1 = Reserva.objects.create(clase=clase_con_hueco, deportista=deportista_padre, estado='CONFIRMADA')
        r2 = Reserva.objects.create(clase=clase_con_hueco, deportista=deportista_hijo, estado='ESPERA')
        
        api_client.force_authenticate(user=deportista_padre)
        res = api_client.delete(f'/api/reservas/{r1.id}/')
        
        # DRF ViewSet ModelViewsset by default returns 204 No Content precisely when destroyed.
        assert res.status_code == 204
        
        r1.refresh_from_db()
        r2.refresh_from_db()
        assert r1.estado == 'CANCELADA'
        assert r2.estado == 'CONFIRMADA'
