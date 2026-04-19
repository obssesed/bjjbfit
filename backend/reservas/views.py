from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import ClaseBJJ, Reserva
from .serializers import ClaseBJJSerializer, ReservaSerializer

class ClaseBJJViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vista que permite listar las clases de BJJ disponibles (Lectura pública).
    Usamos 'prefetch_related' para asegurar que la futura consulta de reservas anidadas no provoque el problema N+1.
    """
    queryset = ClaseBJJ.objects.prefetch_related('reservas').all()
    serializer_class = ClaseBJJSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ReservaViewSet(viewsets.ModelViewSet):
    """
    Vista CRUD completa para gestionar reservas (Crear, Leer, Actualizar, Borrar).
    Usamos 'select_related' para optimizar la carga del deportista y la clase asociada.
    """
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # SEGURIDAD CRÍTICA: Cada usuario solo puede ver y borrar SUS propias reservas.
        return Reserva.objects.select_related('clase', 'deportista').filter(deportista=self.request.user)

    def perform_create(self, serializer):
        # Asigna la reserva, automáticamente, al usuario que hace la petición (Sacado del Token JWT)
        serializer.save(deportista=self.request.user)
