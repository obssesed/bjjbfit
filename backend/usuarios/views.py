from rest_framework import viewsets, permissions
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
        - Otros: Solo usuarios autenticados.
        """
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
