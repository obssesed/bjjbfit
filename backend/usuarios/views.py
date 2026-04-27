from rest_framework import viewsets, permissions
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
