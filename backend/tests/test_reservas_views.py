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

    def test_si_usuario_reserva_clase_pasada_resultado_400(self, api_client, clase_pasada, deportista_adulto_soltero):
        api_client.force_authenticate(user=deportista_adulto_soltero)
        res = api_client.post('/api/reservas/', {'clase': clase_pasada.id})
        assert res.status_code == 400
        assert "ya ha comenzado o finalizado" in str(res.data)

    def test_si_usuario_cancela_fuera_de_tiempo_resultado_400(self, api_client, clase_inminente, deportista_adulto_soltero):
        # A 10 minutos de empezar
        r1 = Reserva.objects.create(clase=clase_inminente, deportista=deportista_adulto_soltero, estado='CONFIRMADA')
        api_client.force_authenticate(user=deportista_adulto_soltero)
        res = api_client.delete(f'/api/reservas/{r1.id}/')
        assert res.status_code == 400
        assert "expira 30 minutos antes" in str(res.data)
        
    def test_si_usuario_soltero_funcionamiento_normal_resultado_confirmada(self, api_client, clase_con_hueco, deportista_adulto_soltero):
        api_client.force_authenticate(user=deportista_adulto_soltero)
        res = api_client.post('/api/reservas/', {'clase': clase_con_hueco.id})
        assert res.status_code == 201

    def test_si_usuario_reserva_misma_clase_dos_veces_resultado_400(self, api_client, clase_con_hueco, deportista_adulto_soltero):
        Reserva.objects.create(clase=clase_con_hueco, deportista=deportista_adulto_soltero, estado='CONFIRMADA')
        api_client.force_authenticate(user=deportista_adulto_soltero)
        res = api_client.post('/api/reservas/', {'clase': clase_con_hueco.id})
        assert res.status_code == 400
        assert "ya tiene una reserva activa" in str(res.data)

@pytest.mark.django_db
class TestClaseBJJViews:
    def test_si_se_envian_parametros_year_y_month_lista_se_filtra_correctamente(self, api_client, admin_user):
        from reservas.models import ClaseBJJ
        from django.utils import timezone
        import datetime
        
        # Crear 3 clases, dos en mayo 2026 y una en junio 2026
        dt_mayo1 = timezone.make_aware(datetime.datetime(2026, 5, 10, 10, 0))
        dt_mayo2 = timezone.make_aware(datetime.datetime(2026, 5, 15, 10, 0))
        dt_junio = timezone.make_aware(datetime.datetime(2026, 6, 10, 10, 0))
        
        ClaseBJJ.objects.create(titulo='BJJ Mayo 1', fecha_hora_inicio=dt_mayo1, fecha_hora_fin=dt_mayo1, capacidad_maxima=20, categoria_acceso='ADULTO')
        ClaseBJJ.objects.create(titulo='BJJ Mayo 2', fecha_hora_inicio=dt_mayo2, fecha_hora_fin=dt_mayo2, capacidad_maxima=20, categoria_acceso='ADULTO')
        ClaseBJJ.objects.create(titulo='BJJ Junio', fecha_hora_inicio=dt_junio, fecha_hora_fin=dt_junio, capacidad_maxima=20, categoria_acceso='ADULTO')
        
        api_client.force_authenticate(user=admin_user)
        
        # Filtrar por mayo
        res_mayo = api_client.get('/api/clases/?year=2026&month=5')
        assert res_mayo.status_code == 200
        assert len(res_mayo.data) == 2
        
        # Filtrar por junio
        res_junio = api_client.get('/api/clases/?year=2026&month=6')
        assert len(res_junio.data) == 1
        assert res_junio.data[0]['titulo'] == 'BJJ Junio'
        
        # Sin filtros debe devolver todo (3 clases)
        res_todo = api_client.get('/api/clases/')
        # Nota: res_todo puede devolver clases de otras fixtures, nos aseguramos que mínimo están las 3 que creamos
        titulos = [c['titulo'] for c in res_todo.data]
        assert 'BJJ Mayo 1' in titulos
        assert 'BJJ Mayo 2' in titulos
        assert 'BJJ Junio' in titulos

    def test_si_se_intenta_crear_clase_duplicada_misma_hora_mismo_tipo_resultado_400(self, api_client, admin_user):
        from reservas.models import ClaseBJJ
        from django.utils import timezone
        import datetime
        
        dt_inicio = timezone.make_aware(datetime.datetime(2026, 7, 10, 10, 0))
        dt_fin = timezone.make_aware(datetime.datetime(2026, 7, 10, 11, 0))
        
        # Clase original
        ClaseBJJ.objects.create(titulo='BJJ Competidor', fecha_hora_inicio=dt_inicio, fecha_hora_fin=dt_fin, capacidad_maxima=20, categoria_acceso='ADULTO')
        
        api_client.force_authenticate(user=admin_user)
        
        # Intentar crear otra clase con el mismo título en la misma fecha_hora_inicio
        payload_duplicado = {
            'titulo': 'BJJ Competidor',
            'descripcion': '',
            'icono': '🥋',
            'categoria_acceso': 'ADULTO',
            'fecha_hora_inicio': dt_inicio.isoformat(),
            'fecha_hora_fin': dt_fin.isoformat(),
            'capacidad_maxima': 20
        }
        res_ko = api_client.post('/api/clases/', payload_duplicado)
        assert res_ko.status_code == 400
        assert "Ya existe una clase de este tipo" in str(res_ko.data)

        # Intentar crear una clase DIFERENTE a la misma hora (esto SI debe estar permitido)
        payload_diferente = {
            'titulo': 'NOGI Principiantes',
            'descripcion': '',
            'icono': '🤼',
            'categoria_acceso': 'ADULTO',
            'fecha_hora_inicio': dt_inicio.isoformat(),
            'fecha_hora_fin': dt_fin.isoformat(),
            'capacidad_maxima': 15
        }
        res_ok = api_client.post('/api/clases/', payload_diferente)
        assert res_ok.status_code == 201
