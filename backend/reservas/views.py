from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db import models
from .models import ClaseBJJ, Reserva
from .serializers import ClaseBJJSerializer, ReservaSerializer

class ClaseBJJViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vista que permite listar las clases de BJJ disponibles (Lectura pública).
    Usamos 'prefetch_related' para asegurar que la futura consulta de reservas anidadas no provoque el problema N+1.
    """
    queryset = ClaseBJJ.objects.prefetch_related('reservas').all()
    serializer_class = ClaseBJJSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ReservaViewSet(viewsets.ModelViewSet):
    """
    Vista CRUD completa para gestionar reservas (Crear, Leer, Actualizar, Borrar).
    Usamos 'select_related' para optimizar la carga del deportista y la clase asociada.
    """
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # SEGURIDAD CRÍTICA: El usuario ve SUS reservas y las de los MENORES DE EDAD A SU CARGO.
        user = self.request.user
        hijos_ids = user.hijos_a_cargo.values_list('id', flat=True)
        return Reserva.objects.select_related('clase', 'deportista').filter(
            models.Q(deportista=user) | models.Q(deportista_id__in=hijos_ids)
        ).order_by('-fecha_reserva')

    def perform_create(self, serializer):
        # Protegiendo creación: Verificamos si mandó deportista. 
        # Si mandó otro ID, tiene que ser su hijo.
        deportista_provisto = serializer.validated_data.get('deportista', None)
        user = self.request.user
        
        if deportista_provisto is None:
            serializer.save(deportista=user)
        else:
            if deportista_provisto != user and deportista_provisto not in user.hijos_a_cargo.all():
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("No tienes permiso para reservar en nombre de este usuario.")
            serializer.save()

    def perform_destroy(self, instance):
        # Lógica de Lista de Espera: Al cancelar una reserva, asciende la primera en espera.
        clase = instance.clase
        
        # En vez de "borrarla", en base a nuestra arquitectura de estados, si el usuario cancela
        # sencillamente actualizamos a CANCELADA.
        instance.estado = 'CANCELADA'
        instance.save()

        # Comprobamos si hay alguien en lista de espera y lo promocionamos si ahora hay plaza.
        if clase.plazas_disponibles() > 0:
            siguiente_en_espera = Reserva.objects.filter(
                clase=clase, estado='ESPERA'
            ).order_by('fecha_reserva').first()
            
            if siguiente_en_espera:
                siguiente_en_espera.estado = 'CONFIRMADA'
                siguiente_en_espera.save()
                # AQUI IRÍAN LAS NOTIFICACIONES PUSH O EMAIL AL USUARIO 'siguiente_en_espera.deportista'
