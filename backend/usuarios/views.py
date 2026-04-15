from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Deportista
from .serializers import DeportistaSerializer

class DeportistaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vista de API (Listar/Leer) para consultar deportistas.
    
    Attributes:
        queryset: Define la consulta base para traer a todos los Deportistas.
        serializer_class: Especifica el serializador a usar para parseo.
        permission_classes: Exige que sólo usuarios autenticados consulten estos datos.
    """
    queryset = Deportista.objects.all()
    serializer_class = DeportistaSerializer
    permission_classes = [IsAuthenticated]
