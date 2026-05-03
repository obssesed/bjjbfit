from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import Deportista, Plan
from .serializers import DeportistaSerializer, PlanSerializer

class DeportistaViewSet(viewsets.ModelViewSet):
    """
    Vista de API para gestionar deportistas.
    Permite el registro público (POST) pero restringe el listado e información sensible.
    """
    queryset = Deportista.objects.all()
    serializer_class = DeportistaSerializer

    def get_permissions(self):
        """
        Asigna permisos dinámicos según la acción:
        - 'create': Público (Registro).
        - 'activos_backoffice': Solo administradores.
        - Otros: Solo usuarios autenticados.
        """
        if self.action == 'create':
            return [permissions.AllowAny()]
        if self.action == 'activos_backoffice':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Devuelve el perfil del usuario actualmente logueado.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def activos_backoffice(self, request):
        """
        Endpoint exclusivo para el Backoffice. Devuelve todos los usuarios 
        con plan_activo=True, ordenados alfabéticamente por nombre.
        """
        activos = Deportista.objects.filter(plan_activo=True).order_by('first_name', 'last_name')
        serializer = self.get_serializer(activos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def inactivos_backoffice(self, request):
        """
        Endpoint exclusivo para el Backoffice. Devuelve todos los usuarios 
        con plan_activo=False y que ya tengan un tipo_plan asignado (bajas).
        """
        inactivos = Deportista.objects.filter(plan_activo=False, tipo_plan__isnull=False).order_by('first_name', 'last_name')
        serializer = self.get_serializer(inactivos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def pendientes_backoffice(self, request):
        """
        Endpoint exclusivo para el Backoffice. Devuelve todos los usuarios 
        con plan_activo=False y que nunca han tenido un tipo_plan asignado (nuevos).
        """
        pendientes = Deportista.objects.filter(plan_activo=False, tipo_plan__isnull=True, is_staff=False).order_by('-date_joined')
        serializer = self.get_serializer(pendientes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def activar_plan(self, request, pk=None):
        """
        Activa un bono para un usuario específico.
        Recibe: tipo_plan (ADULTO|JUVENIL|INFANTIL) y es_familiar (bool).
        """
        deportista = self.get_object()
        plan_id = request.data.get('plan_id')
        es_familiar = request.data.get('es_familiar', False)
        
        try:
            plan = Plan.objects.get(id=plan_id)
        except (Plan.DoesNotExist, ValueError):
            return Response(
                {'error': 'Plan no encontrado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deportista.tipo_plan = plan
        deportista.es_familiar = bool(es_familiar)
        deportista.plan_activo = True
        deportista.save()
        
        return Response({'success': f'Plan {plan.nombre} activado correctamente para {deportista.first_name or deportista.username}.'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def dar_baja(self, request, pk=None):
        """
        Desactiva el plan de un deportista (pasa a estado Baja/Inactivo).
        """
        deportista = self.get_object()
        deportista.plan_activo = False
        deportista.save()
        
        return Response({'success': f'{deportista.first_name or deportista.username} dado de baja correctamente.'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def cambiar_plan(self, request, pk=None):
        """
        Cambia el tipo de plan de un deportista activo sin tocar plan_activo.
        """
        deportista = self.get_object()
        plan_id = request.data.get('plan_id')
        es_familiar = request.data.get('es_familiar', False)
        
        try:
            plan = Plan.objects.get(id=plan_id)
        except (Plan.DoesNotExist, ValueError):
            return Response(
                {'error': 'Plan no encontrado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deportista.tipo_plan = plan
        deportista.es_familiar = bool(es_familiar)
        deportista.plan_activo = True # Al activar plan, marcamos como activo
        deportista.save()
        
        return Response({'success': f'Plan {plan.nombre} activado correctamente para {deportista.first_name or deportista.username}.'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def actualizar_graduacion(self, request, pk=None):
        """
        Permite al profesor subir de grado o cambiar el cinturón de un atleta.
        Si el cinturón cambia, los grados se resetean a 0 automáticamente.
        """
        deportista = self.get_object()
        nuevo_cinturon = request.data.get('cinturon')
        nuevos_grados = request.data.get('grados')

        if nuevo_cinturon is not None:
            # Si el cinturón cambia, asignamos el nuevo cinturón y los grados (o 0 por defecto)
            if nuevo_cinturon != deportista.cinturon:
                deportista.cinturon = nuevo_cinturon
                deportista.grados = nuevos_grados if nuevos_grados is not None else 0
            elif nuevos_grados is not None:
                # Si es el mismo cinturón, solo actualizamos grados
                deportista.grados = nuevos_grados
            
            deportista.fecha_ultima_graduacion = timezone.now().date()
            deportista.save()
            return Response({'success': f'Graduación de {deportista.first_name} actualizada correctamente.'})
        
        return Response({'error': 'Faltan datos para la graduación.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def actualizar_id_interno(self, request, pk=None):
        """
        Permite al profesor cambiar el Nº de Socio (id_interno) de un atleta.
        """
        deportista = self.get_object()
        nuevo_id = request.data.get('id_interno')
        
        deportista.id_interno = nuevo_id
        deportista.save()
        return Response({'success': f'Nº Socio de {deportista.first_name} actualizado a {nuevo_id}.'})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def reporte_ingresos(self, request):
        """
        Calcula una estimación de ingresos en tiempo real basada en los planes
        activos actuales y la antigüedad de los usuarios (mes actual, -1, -2).
        Aplica el 50% de descuento a las cuentas marcadas como 'es_familiar'.
        """
        hoy = timezone.now().date()
        mes_actual = hoy.replace(day=1)
        
        # Retroceder 1 mes
        ultimo_dia_mes_ant = mes_actual - timezone.timedelta(days=1)
        mes_anterior = ultimo_dia_mes_ant.replace(day=1)
        
        # Retroceder 2 meses
        ultimo_dia_hace_2 = mes_anterior - timezone.timedelta(days=1)
        hace_dos_meses = ultimo_dia_hace_2.replace(day=1)
        
        MESES_ES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        usuarios = Deportista.objects.filter(is_staff=False, plan_activo=True).exclude(tipo_plan__isnull=True)
        
        data_actual = {'total': Decimal('0.00'), 'activos': 0, 'familiares': 0, 'desglose': {}}
        data_anterior = {'total': Decimal('0.00'), 'activos': 0, 'familiares': 0, 'desglose': {}}
        data_hace_2 = {'total': Decimal('0.00'), 'activos': 0, 'familiares': 0, 'desglose': {}}
        
        def registrar_ingreso(data_mes, plan_nombre, precio, es_fam):
            data_mes['total'] += precio
            data_mes['activos'] += 1
            if es_fam:
                data_mes['familiares'] += 1
            if plan_nombre not in data_mes['desglose']:
                data_mes['desglose'][plan_nombre] = {'cantidad': 0, 'ingresos': Decimal('0.00')}
            data_mes['desglose'][plan_nombre]['cantidad'] += 1
            data_mes['desglose'][plan_nombre]['ingresos'] += precio

        for u in usuarios:
            precio = u.tipo_plan.precio_base
            plan_nombre = u.tipo_plan.nombre
            es_fam = u.es_familiar
            
            if es_fam:
                precio = precio * Decimal('0.5')
                
            # Siempre se cobra en el mes actual si están activos hoy
            registrar_ingreso(data_actual, plan_nombre, precio, es_fam)
            
            # Si se dieron de alta antes del día 1 del mes actual, se asume que pagaron el mes anterior
            if u.date_joined.date() < mes_actual:
                registrar_ingreso(data_anterior, plan_nombre, precio, es_fam)
                
            # Si se dieron de alta antes del día 1 del mes anterior, pagaron hace 2 meses
            if u.date_joined.date() < mes_anterior:
                registrar_ingreso(data_hace_2, plan_nombre, precio, es_fam)
                
        def format_response(data_mes, etiqueta):
            desglose = []
            for nombre, stats in data_mes['desglose'].items():
                desglose.append({
                    'plan': nombre,
                    'cantidad': stats['cantidad'],
                    'ingresos': float(stats['ingresos'])
                })
            desglose.sort(key=lambda x: x['plan'])

            return {
                'etiqueta': etiqueta,
                'total': float(data_mes['total']),
                'usuarios_activos': data_mes['activos'],
                'usuarios_familiares': data_mes['familiares'],
                'desglose': desglose
            }
                
        return Response({
            'mes_actual': format_response(data_actual, f"{MESES_ES[hoy.month-1]} {hoy.year}"),
            'mes_anterior': format_response(data_anterior, f"{MESES_ES[mes_anterior.month-1]} {mes_anterior.year}"),
            'hace_dos_meses': format_response(data_hace_2, f"{MESES_ES[hace_dos_meses.month-1]} {hace_dos_meses.year}")
        })

class PlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que el administrador gestione los planes (CRUD).
    """
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # Solo admin puede crear/editar/borrar. Todos pueden ver (para el registro).
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


