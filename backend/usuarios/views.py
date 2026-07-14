from django.utils import timezone
import datetime
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from .models import Deportista, Plan, Notificacion, SolicitudReseteoPassword
from .serializers import DeportistaSerializer, PlanSerializer, NotificacionSerializer, SolicitudReseteoPasswordSerializer

class DeportistaViewSet(viewsets.ModelViewSet):
    """
    Vista de API para gestionar deportistas.
    Permite el registro público (POST) pero restringe el listado e información sensible.
    """
    queryset = Deportista.objects.all()
    serializer_class = DeportistaSerializer

    def get_queryset(self):
        """
        Administradores ven todo. Usuarios normales solo se ven a sí mismos y a sus hijos.
        """
        user = self.request.user
        if not user or user.is_anonymous:
            return Deportista.objects.none()
            
        if user.is_staff:
            return Deportista.objects.all().select_related('tipo_plan', 'padre_tutor').prefetch_related('hijos_a_cargo')
            
        if self.action == 'actualizar_perfil_hijo':
            return Deportista.objects.all().select_related('tipo_plan', 'padre_tutor').prefetch_related('hijos_a_cargo')

        hijos_ids = user.hijos_a_cargo.values_list('id', flat=True)
        return Deportista.objects.filter(
            models.Q(id=user.id) | models.Q(id__in=hijos_ids)
        ).select_related('tipo_plan', 'padre_tutor').prefetch_related('hijos_a_cargo')

    def get_permissions(self):
        """
        Asigna permisos dinámicos según la acción:
        - 'create', 'solicitar_reseteo': Público.
        - 'list', 'activos_backoffice', etc: Solo administradores.
        - Otros (retrieve, me, etc): Solo usuarios autenticados (get_queryset se encarga del resto).
        """
        if self.action in ['create', 'solicitar_reseteo']:
            return [permissions.AllowAny()]
            
        if self.action in ['list', 'activos_backoffice', 'inactivos_backoffice', 'pendientes_backoffice', 'activar_plan', 'crear_alta_manual']:
            return [permissions.IsAdminUser()]
            
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def solicitar_reseteo(self, request):
        username = request.data.get('username')
        if not username:
            return Response({"error": "Debes proporcionar un nombre de usuario."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Deportista.objects.get(username=username)
            # Solo crear si no hay una pendiente
            if not SolicitudReseteoPassword.objects.filter(usuario=user, resuelta=False).exists():
                SolicitudReseteoPassword.objects.create(usuario=user)
            # Siempre devolvemos éxito por seguridad (para no revelar si el user existe o no si no queremos, aunque aquí sí lo verificamos)
            return Response({"status": "Solicitud enviada correctamente."})
        except Deportista.DoesNotExist:
            # Fingimos éxito por seguridad
            return Response({"status": "Solicitud enviada correctamente."})

    @action(detail=False, methods=['post'])
    def cambiar_password_obligatorio(self, request):
        user = request.user
        new_password = request.data.get('new_password')
        
        if not new_password or len(new_password) < 6:
            return Response({"error": "La contraseña debe tener al menos 6 caracteres."}, status=status.HTTP_400_BAD_REQUEST)
            
        if not user.requiere_cambio_password:
            return Response({"error": "No requieres un cambio de contraseña obligatorio."}, status=status.HTTP_400_BAD_REQUEST)
            
        user.password = make_password(new_password)
        user.requiere_cambio_password = False
        user.save()
        return Response({"status": "Contraseña actualizada correctamente."})

    @action(detail=False, methods=['get', 'patch', 'put'])
    def me(self, request):
        """
        Devuelve o actualiza el perfil del usuario actualmente logueado.
        """
        if request.method in ['PATCH', 'PUT']:
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
        
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def actualizar_perfil_hijo(self, request, pk=None):
        """
        Permite a un padre/tutor actualizar los datos de su hijo si este es menor de 14 años.
        """
        hijo = self.get_object()
        
        # 1. Verificar que el usuario logueado es el tutor
        if hijo.padre_tutor != request.user:
            return Response({"error": "No tienes permiso para editar este perfil."}, status=status.HTTP_403_FORBIDDEN)
        
        # 2. Verificar que el hijo tiene < 14 años
        if hijo.fecha_nacimiento:
            hoy = datetime.date.today()
            edad = hoy.year - hijo.fecha_nacimiento.year - ((hoy.month, hoy.day) < (hijo.fecha_nacimiento.month, hijo.fecha_nacimiento.day))
            if edad >= 14:
                return Response({"error": "El alumno ya tiene 14 años o más y debe gestionar su propio perfil."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(hijo, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def crear_perfil_hijo(self, request):
        """
        Permite a un padre/tutor registrar un nuevo perfil para un hijo menor de 14 años.
        """
        padre = request.user
        data = request.data.copy()
        
        # Validación básica de edad
        fecha_nacStr = data.get('fecha_nacimiento')
        if not fecha_nacStr:
            return Response({"error": "La fecha de nacimiento es obligatoria."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            import datetime
            fecha_nac = datetime.datetime.strptime(fecha_nacStr, '%Y-%m-%d').date()
            hoy = datetime.date.today()
            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            if edad >= 14:
                return Response({"error": "Solo puedes crear perfiles a tu cargo para menores de 14 años."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Fecha de nacimiento inválida."}, status=status.HTTP_400_BAD_REQUEST)

        # Configurar datos del hijo
        # Para que no choque, el username del hijo puede ser autogenerado o proporcionado.
        username = data.get('username')
        if not username:
            # Autogenerar un username base si no lo envían
            import uuid
            username = f"menor_{uuid.uuid4().hex[:6]}"
            data['username'] = username
            
        data['padre_tutor'] = padre.id
        # Los menores usan el NIF/DNI del padre por regla de negocio
        data['nif'] = padre.nif
        
        # El menor necesita un email único por reglas del modelo
        if 'email' not in data or not data['email']:
            data['email'] = f"{username}@dependiente.bjjbfit.com"
        
        # El serializer por defecto (DeportistaSerializer) puede fallar por falta de password
        # si no se proporciona. Generamos un password aleatorio irrelevante ya que el padre lo gestiona.
        if 'password' not in data:
            data['password'] = uuid.uuid4().hex

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        hijo = serializer.save(padre_tutor=padre)
        
        return Response(self.get_serializer(hijo).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def crear_alta_manual(self, request):
        """
        Endpoint exclusivo para el Backoffice. Permite a los administradores
        dar de alta usuarios manualmente, asignándoles un plan activo y
        forzándoles a cambiar su contraseña por defecto al primer login.
        """
        data = request.data.copy()
        
        # Generar un username si no se envía o si se quiere autogenerar
        import uuid
        if not data.get('username'):
            data['username'] = f"user_{uuid.uuid4().hex[:6]}"
            
        # Asignar contraseña por defecto si no se ha enviado una
        if 'password' not in data:
            data['password'] = 'Bjjbfit2026!'
        
        # Validar y guardar con el serializer (ignora campos read_only)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        nuevo_usuario = serializer.save()
        
        # Asignar campos read_only que el admin sí puede setear aquí
        nuevo_usuario.set_password(data['password'])
        nuevo_usuario.requiere_cambio_password = True
        
        if 'plan_activo' in request.data:
            nuevo_usuario.plan_activo = str(request.data['plan_activo']).lower() == 'true'
            
        if 'es_familiar' in request.data:
            nuevo_usuario.es_familiar = str(request.data['es_familiar']).lower() == 'true'
            
        if 'cinturon' in request.data:
            nuevo_usuario.cinturon = request.data['cinturon']
            
        if 'tipo_plan' in request.data and request.data['tipo_plan']:
            try:
                plan = Plan.objects.get(id=request.data['tipo_plan'])
                nuevo_usuario.tipo_plan = plan
            except Plan.DoesNotExist:
                pass
                
        nuevo_usuario.save()
        
        return Response({
            'success': f'Usuario {nuevo_usuario.first_name} creado con éxito.',
            'usuario': self.get_serializer(nuevo_usuario).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def activos_backoffice(self, request):
        """
        Endpoint exclusivo para el Backoffice. Devuelve todos los usuarios 
        con plan_activo=True, ordenados alfabéticamente por nombre.
        """
        activos = Deportista.objects.filter(plan_activo=True).select_related('tipo_plan', 'padre_tutor').prefetch_related('hijos_a_cargo').order_by('first_name', 'last_name')
        serializer = self.get_serializer(activos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def inactivos_backoffice(self, request):
        """
        Endpoint exclusivo para el Backoffice. Devuelve todos los usuarios 
        con plan_activo=False y que ya tengan un tipo_plan asignado (bajas).
        """
        inactivos = Deportista.objects.filter(plan_activo=False, tipo_plan__isnull=False).select_related('tipo_plan', 'padre_tutor').prefetch_related('hijos_a_cargo').order_by('first_name', 'last_name')
        serializer = self.get_serializer(inactivos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def pendientes_backoffice(self, request):
        """
        Endpoint exclusivo para el Backoffice. Devuelve todos los usuarios 
        con plan_activo=False y que nunca han tenido un tipo_plan asignado (nuevos).
        """
        pendientes = Deportista.objects.filter(plan_activo=False, tipo_plan__isnull=True, is_staff=False).select_related('tipo_plan', 'padre_tutor').prefetch_related('hijos_a_cargo').order_by('-date_joined')
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

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
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
                deportista.grados = 0
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

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def actualizar_nif(self, request, pk=None):
        """
        Permite al administrador actualizar el DNI/NIF de un deportista.
        """
        deportista = self.get_object()
        nuevo_nif = request.data.get('nif', '').strip()

        if not nuevo_nif:
            return Response({'error': 'El DNI/NIF no puede estar vacío.'}, status=status.HTTP_400_BAD_REQUEST)

        deportista.nif = nuevo_nif
        deportista.save()
        return Response({'success': f'DNI de {deportista.first_name} actualizado a {nuevo_nif}.'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def actualizar_nombre(self, request, pk=None):
        """
        Permite al administrador corregir el nombre y/o apellidos de un deportista.
        """
        deportista = self.get_object()
        nuevo_nombre = request.data.get('first_name', '').strip()
        nuevo_apellido = request.data.get('last_name', '').strip()

        if not nuevo_nombre and not nuevo_apellido:
            return Response(
                {'error': 'Debes proporcionar al menos un nombre o apellido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        deportista.first_name = nuevo_nombre
        deportista.last_name = nuevo_apellido
        deportista.save()
        nombre_completo = f'{nuevo_nombre} {nuevo_apellido}'.strip()
        return Response({'success': f'Nombre actualizado a {nombre_completo}.'})

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
        
        usuarios = Deportista.objects.filter(is_staff=False, plan_activo=True).exclude(tipo_plan__isnull=True).select_related('tipo_plan')
        
        data_actual = {'total': Decimal('0.00'), 'activos': 0, 'familiares': 0, 'fundadores': 0, 'desglose': {}, 'sexo': {}}
        data_anterior = {'total': Decimal('0.00'), 'activos': 0, 'familiares': 0, 'fundadores': 0, 'desglose': {}, 'sexo': {}}
        data_hace_2 = {'total': Decimal('0.00'), 'activos': 0, 'familiares': 0, 'fundadores': 0, 'desglose': {}, 'sexo': {}}
        
        def registrar_ingreso(data_mes, plan_nombre, precio, es_fam, sexo_val, es_fundador):
            data_mes['total'] += precio
            data_mes['activos'] += 1
            if es_fam:
                data_mes['familiares'] += 1
            if es_fundador:
                data_mes['fundadores'] += 1
            
            if plan_nombre not in data_mes['desglose']:
                data_mes['desglose'][plan_nombre] = {'cantidad': 0, 'ingresos': Decimal('0.00')}
            data_mes['desglose'][plan_nombre]['cantidad'] += 1
            data_mes['desglose'][plan_nombre]['ingresos'] += precio

            # Agrupar por sexo
            s_key = sexo_val if sexo_val in ['M', 'F'] else 'No Especificado'
            if s_key not in data_mes['sexo']:
                data_mes['sexo'][s_key] = 0
            data_mes['sexo'][s_key] += 1

        fecha_limite_fundador = datetime.date(2025, 12, 31)

        for u in usuarios:
            precio = u.tipo_plan.precio_base
            plan_nombre = u.tipo_plan.nombre
            es_fam = u.es_familiar
            sexo_val = u.sexo
            
            # Es fundador si se dio de alta antes o igual al 31/12/2025, o si su plan ya dice Fundador
            es_fundador = u.date_joined.date() <= fecha_limite_fundador or 'Fundador' in plan_nombre
            
            # Si por algún motivo no tiene asignado el plan fundador pero cumple la fecha
            # podríamos aplicar el descuento, pero asumimos que el precio de su plan ya es el correcto 
            # (asignado por admin o por el script).
            
            if es_fam:
                precio = precio * Decimal('0.5')
                
            # Siempre se cobra en el mes actual si están activos hoy
            registrar_ingreso(data_actual, plan_nombre, precio, es_fam, sexo_val, es_fundador)
            
            # Si se dieron de alta antes del día 1 del mes actual, se asume que pagaron el mes anterior
            if u.date_joined.date() < mes_actual:
                registrar_ingreso(data_anterior, plan_nombre, precio, es_fam, sexo_val, es_fundador)
                
            # Si se dieron de alta antes del día 1 del mes anterior, pagaron hace 2 meses
            if u.date_joined.date() < mes_anterior:
                registrar_ingreso(data_hace_2, plan_nombre, precio, es_fam, sexo_val, es_fundador)
                
        def format_response(data_mes, etiqueta):
            desglose = []
            for nombre, stats in data_mes['desglose'].items():
                desglose.append({
                    'plan': nombre,
                    'cantidad': stats['cantidad'],
                    'ingresos': float(stats['ingresos'])
                })
            desglose.sort(key=lambda x: x['plan'])

            desglose_sexo = []
            for k, v in data_mes['sexo'].items():
                desglose_sexo.append({
                    'sexo': 'Masculino' if k == 'M' else ('Femenino' if k == 'F' else k),
                    'cantidad': v
                })
            desglose_sexo.sort(key=lambda x: x['sexo'])

            return {
                'etiqueta': etiqueta,
                'total': float(data_mes['total']),
                'usuarios_activos': data_mes['activos'],
                'usuarios_familiares': data_mes['familiares'],
                'usuarios_fundadores': data_mes['fundadores'],
                'desglose': desglose,
                'desglose_sexo': desglose_sexo
            }
                
        return Response({
            'mes_actual': format_response(data_actual, f"{MESES_ES[hoy.month-1]} {hoy.year}"),
            'mes_anterior': format_response(data_anterior, f"{MESES_ES[mes_anterior.month-1]} {mes_anterior.year}"),
            'hace_dos_meses': format_response(data_hace_2, f"{MESES_ES[hace_dos_meses.month-1]} {hace_dos_meses.year}")
        })

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def reporte_anual(self, request):
        """
        Retorna la evolución de los últimos 12 meses (usuarios activos e ingresos estimados).
        """
        hoy = timezone.now().date()
        MESES_ES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        meses = []
        fecha_iter = hoy.replace(day=1)
        
        for _ in range(12):
            meses.append({
                'fecha_corte': fecha_iter,
                'etiqueta': f"{MESES_ES[fecha_iter.month-1]} {fecha_iter.year}",
                'activos': 0,
                'total': Decimal('0.00')
            })
            # Retroceder 1 mes
            ultimo_dia_mes_ant = fecha_iter - timezone.timedelta(days=1)
            fecha_iter = ultimo_dia_mes_ant.replace(day=1)
            
        usuarios = Deportista.objects.filter(is_staff=False, plan_activo=True).exclude(tipo_plan__isnull=True).select_related('tipo_plan')
        
        for u in usuarios:
            precio = u.tipo_plan.precio_base
            if u.es_familiar:
                precio = precio * Decimal('0.5')
                
            fecha_alta = u.date_joined.date()
            
            for m in meses:
                # Si el usuario se unió ANTES del día 1 del "mes siguiente" a m['fecha_corte']
                # Para simplificar, asumimos que todos los activos actuales pagaron en todos los meses pasados
                # en los que ya estaban dados de alta.
                # m['fecha_corte'] es el día 1 de ese mes.
                # Si se unió en Mayo o antes de Mayo, paga Mayo.
                # Técnicamente si date_joined < (m['fecha_corte'] + 1 mes)
                
                # Para calcular el inicio del mes siguiente al m['fecha_corte']
                if m['fecha_corte'].month == 12:
                    inicio_mes_siguiente = m['fecha_corte'].replace(year=m['fecha_corte'].year+1, month=1)
                else:
                    inicio_mes_siguiente = m['fecha_corte'].replace(month=m['fecha_corte'].month+1)
                
                if fecha_alta < inicio_mes_siguiente:
                    m['activos'] += 1
                    m['total'] += precio

        # Convertir a formato de respuesta y ordenar cronológicamente (el más antiguo primero)
        resultado = []
        for m in reversed(meses):
            resultado.append({
                'etiqueta': m['etiqueta'],
                'activos': m['activos'],
                'total': float(m['total'])
            })
            
        return Response(resultado)

class PlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que el administrador gestione los planes (CRUD).
    """
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # Solo admin puede crear/editar/borrar. Todos pueden ver (para el registro y la landing).
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]



class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Notificacion.objects.all()
        return Notificacion.objects.filter(
            models.Q(es_global=True) | models.Q(destinatario=user)
        ).distinct()

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        user = request.user
        
        # Las notificaciones globales no se muestran al staff (admin) en el modal bloqueante,
        # ya que suelen ser ellos quienes las generan.
        if user.is_staff:
            globales_pendientes = Notificacion.objects.none()
        else:
            globales_pendientes = Notificacion.objects.filter(es_global=True).exclude(leida_por=user)
            
        personales_pendientes = Notificacion.objects.filter(destinatario=user, leida=False)
        
        pendientes = (globales_pendientes | personales_pendientes).distinct().order_by('-fecha_creacion')
        serializer = self.get_serializer(pendientes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def leer(self, request, pk=None):
        notificacion = self.get_object()
        user = request.user
        
        if notificacion.es_global:
            notificacion.leida_por.add(user)
        else:
            if notificacion.destinatario == user:
                notificacion.leida = True
                notificacion.save()
            else:
                return Response({"error": "No puedes leer esta notificación."}, status=403)
        
        return Response({"status": "leida"})

class SolicitudReseteoViewSet(viewsets.ModelViewSet):
    """
    ViewSet exclusivo para administradores para gestionar las solicitudes de reseteo.
    """
    queryset = SolicitudReseteoPassword.objects.all()
    serializer_class = SolicitudReseteoPasswordSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        # Por defecto devolvemos solo las pendientes, a menos que se pida todo
        if self.request.query_params.get('todas') == 'true':
            return self.queryset
        return self.queryset.filter(resuelta=False)

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        solicitud = self.get_object()
        if solicitud.resuelta:
            return Response({"error": "La solicitud ya ha sido resuelta."}, status=status.HTTP_400_BAD_REQUEST)
            
        usuario = solicitud.usuario
        # Generar contraseña temporal segura
        temp_password = get_random_string(8, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
        
        # Actualizar usuario
        usuario.password = make_password(temp_password)
        usuario.requiere_cambio_password = True
        usuario.save()
        
        # Marcar solicitud como resuelta
        solicitud.resuelta = True
        solicitud.fecha_resolucion = timezone.now()
        solicitud.save()
        
        return Response({
            "status": "Solicitud aprobada.",
            "temp_password": temp_password,
            "username": usuario.username
        })
