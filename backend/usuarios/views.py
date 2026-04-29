from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Deportista
from .serializers import DeportistaSerializer

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
        tipo_plan = request.data.get('tipo_plan')
        es_familiar = request.data.get('es_familiar', False)
        
        planes_validos = ['ADULTO', 'JUVENIL', 'INFANTIL']
        if tipo_plan not in planes_validos:
            return Response(
                {'error': f'Tipo de plan inválido. Opciones: {", ".join(planes_validos)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deportista.plan_activo = True
        deportista.tipo_plan = tipo_plan
        deportista.es_familiar = bool(es_familiar)
        deportista.save()
        
        etiqueta = f"Mensual {tipo_plan.capitalize()}"
        if es_familiar:
            etiqueta += " Familiar"
        
        return Response({'success': f'{etiqueta} activado correctamente para {deportista.first_name or deportista.username}.'})

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
        tipo_plan = request.data.get('tipo_plan')
        es_familiar = request.data.get('es_familiar', False)
        
        planes_validos = ['ADULTO', 'JUVENIL', 'INFANTIL']
        if tipo_plan not in planes_validos:
            return Response(
                {'error': f'Tipo de plan inválido. Opciones: {", ".join(planes_validos)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deportista.tipo_plan = tipo_plan
        deportista.es_familiar = bool(es_familiar)
        deportista.save()
        
        etiqueta = f"Mensual {tipo_plan.capitalize()}"
        if es_familiar:
            etiqueta += " Familiar"
        
        return Response({'success': f'Plan cambiado a {etiqueta} para {deportista.first_name or deportista.username}.'})
