from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError
from .models import ClaseBJJ, Reserva, PlantillaClase
from .serializers import ClaseBJJSerializer, ReservaSerializer, PlantillaClaseSerializer
import datetime

class ClaseBJJViewSet(viewsets.ModelViewSet):
    """
    Vista que permite listar las clases de BJJ disponibles.
    Permisos: Lectura para todos, escritura solo para STAFF.
    """
    queryset = ClaseBJJ.objects.prefetch_related('reservas__deportista').all()
    serializer_class = ClaseBJJSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        if year and month:
            qs = qs.filter(fecha_hora_inicio__year=year, fecha_hora_inicio__month=month)
        return qs.order_by('fecha_hora_inicio')

class PlantillaClaseViewSet(viewsets.ModelViewSet):
    queryset = PlantillaClase.objects.all()
    serializer_class = PlantillaClaseSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def propagar(self, request, pk=None):
        plantilla = self.get_object()
        fecha_inicio_str = request.data.get('fecha_inicio')
        fecha_fin_str = request.data.get('fecha_fin')
        dias_semana = request.data.get('dias_semana', []) # List of ints 0-6 (Mon-Sun)

        if not fecha_inicio_str or not fecha_fin_str:
            return Response({'error': 'Faltan fechas de inicio/fin'}, status=400)

        fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()

        clases_creadas = 0
        curr = fecha_inicio
        while curr <= fecha_fin:
            if curr.weekday() in dias_semana:
                # Combinar fecha con hora de la plantilla
                dt_inicio = datetime.datetime.combine(curr, plantilla.hora_inicio)
                dt_fin = dt_inicio + datetime.timedelta(minutes=plantilla.duracion_minutos)
                
                # Evitar duplicados exactos en el mismo momento
                if not ClaseBJJ.objects.filter(titulo=plantilla.titulo, fecha_hora_inicio=dt_inicio).exists():
                    ClaseBJJ.objects.create(
                        titulo=plantilla.titulo,
                        descripcion=plantilla.descripcion,
                        icono=plantilla.icono,
                        imagen_icono=plantilla.imagen_icono,
                        categoria_acceso=plantilla.categoria_acceso,
                        fecha_hora_inicio=dt_inicio,
                        fecha_hora_fin=dt_fin,
                        capacidad_maxima=plantilla.capacidad_maxima
                    )
                    clases_creadas += 1
            curr += datetime.timedelta(days=1)

        return Response({'success': f'Se han generado {clases_creadas} clases correctamente.'})

class ReservaViewSet(viewsets.ModelViewSet):
    """
    Vista CRUD completa para gestionar reservas (Crear, Leer, Actualizar, Borrar).
    Usamos 'select_related' para optimizar la carga del deportista y la clase asociada.
    """
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Administradores ven TODO. Usuarios normales ven lo suyo y sus hijos.
        """
        user = self.request.user
        if user.is_staff:
            return Reserva.objects.select_related('clase', 'deportista').all().order_by('-fecha_reserva')
            
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
        # Regla de Negocio: Cancelaciones solo hasta 30 mins antes.
        # EXCEPCIÓN: Los administradores pueden cancelar en cualquier momento.
        user = self.request.user
        if not user.is_staff:
            tiempo_limite = instance.clase.fecha_hora_inicio - timedelta(minutes=30)
            if timezone.now() > tiempo_limite:
                raise ValidationError("Demasiado tarde para cancelar. La ventana de cancelación expira 30 minutos antes del inicio.")

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
