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
        con plan_activo=False y que hayan tenido reservas (inactivos históricos).
        """
        inactivos = Deportista.objects.filter(plan_activo=False, mis_reservas__isnull=False).distinct().order_by('first_name', 'last_name')
        serializer = self.get_serializer(inactivos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def pendientes_backoffice(self, request):
        """
        Endpoint exclusivo para el Backoffice. Devuelve todos los usuarios 
        con plan_activo=False y sin historial de reservas (recién registrados).
        """
        pendientes = Deportista.objects.filter(plan_activo=False, mis_reservas__isnull=True, is_staff=False).distinct().order_by('-date_joined')
        serializer = self.get_serializer(pendientes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def activar_plan(self, request, pk=None):
        """
        Activa un bono (MENSUAL o FAMILIAR) para un usuario específico.
        """
        deportista = self.get_object()
        tipo_plan = request.data.get('tipo_plan')
        
        if tipo_plan not in ['MENSUAL', 'FAMILIAR']:
            return Response({'error': 'Tipo de plan inválido o no especificado'}, status=status.HTTP_400_BAD_REQUEST)
        
        deportista.plan_activo = True
        deportista.tipo_plan = tipo_plan
        deportista.save()
        
        return Response({'success': f'Plan {tipo_plan} activado correctamente'})
