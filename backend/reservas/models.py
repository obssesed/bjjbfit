from django.db import models
from usuarios.models import Deportista

class ClaseBJJ(models.Model):
    """
    Modelo que representa una sesión o clase de BJJ disponible en el gimnasio.
    """
    titulo = models.CharField(
        max_length=100, 
        help_text="Nombre corto de la clase (ej. BJJ Fundamentos, No-Gi)."
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción o detalles adicionales sobre la sesión."
    )
    fecha_hora_inicio = models.DateTimeField(
        help_text="Fecha y hora de inicio de la clase."
    )
    fecha_hora_fin = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora de finalización de la clase."
    )
    capacidad_maxima = models.PositiveIntegerField(
        default=30,
        help_text="Número máximo de personas que pueden asistir a la clase."
    )
    icono = models.CharField(
        max_length=50,
        default="🥋",
        help_text="Icono visual para la clase (emoji o nombre de icono)."
    )

    def plazas_ocupadas(self) -> int:
        """Devuelve el total de reservas activas"""
        return self.reservas.filter(estado='CONFIRMADA').count()

    def en_espera(self) -> int:
        """Devuelve el total de personas en lista de espera"""
        return self.reservas.filter(estado='ESPERA').count()

    def plazas_disponibles(self) -> int:
        """
        Calcula el número de plazas disponibles para la clase actual.
        """
        return self.capacidad_maxima - self.plazas_ocupadas()

    def __str__(self) -> str:
        return f"{self.icono} {self.titulo} - {self.fecha_hora_inicio.strftime('%Y-%m-%d %H:%M')}"

class PlantillaClase(models.Model):
    """
    Molde para generar clases repetitivas.
    """
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    icono = models.CharField(max_length=50, default="🥋")
    hora_inicio = models.TimeField(help_text="Hora de comienzo por defecto.")
    duracion_minutos = models.PositiveIntegerField(default=90)
    capacidad_maxima = models.PositiveIntegerField(default=30)

    def __str__(self):
        return f"Plantilla: {self.icono} {self.titulo} ({self.hora_inicio})"


class Reserva(models.Model):
    """
    Modelo que representa la asistencia de un Deportista a una ClaseBJJ.
    """
    ESTADOS_RESERVA = [
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
        ('ESPERA', 'Lista de Espera'),
    ]

    clase = models.ForeignKey(
        ClaseBJJ, 
        on_delete=models.CASCADE, 
        related_name="reservas",
        help_text="La clase de BJJ a la que asiste el deportista."
    )
    deportista = models.ForeignKey(
        Deportista, 
        on_delete=models.CASCADE, 
        related_name="mis_reservas",
        help_text="El deportista que realiza la reserva."
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_RESERVA,
        default='CONFIRMADA',
        help_text="Estado actual de la reserva gestionando aforo y lista de espera."
    )
    fecha_reserva = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora exactas en que se guardó este registro."
    )

    class Meta:
        """
        Evita que el mismo usuario reserve dos veces la misma clase.
        """
        unique_together = ('clase', 'deportista')

    def __str__(self) -> str:
        """
        Representación en texto de la reserva.
        """
        return f"Reserva [{self.get_estado_display()}]: {self.deportista} -> {self.clase.titulo}"
