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
    fecha_hora_inicio = models.DateTimeField(
        help_text="Fecha y hora de inicio de la clase."
    )
    capacidad_maxima = models.PositiveIntegerField(
        default=30,
        help_text="Número máximo de personas que pueden asistir a la clase."
    )

    def plazas_disponibles(self) -> int:
        """
        Calcula el número de plazas disponibles para la clase actual.
        (Ejemplo de lógica en el 'Fat Model')

        Returns:
            int: Entero que representa la diferencia entre la capacidad máxima 
                 y el total de reservas activas.
        """
        reservas_actuales = self.reservas.count()
        return self.capacidad_maxima - reservas_actuales

    def __str__(self) -> str:
        """
        Retorna una cadena legible para el administrador.
        """
        return f"{self.titulo} - {self.fecha_hora_inicio.strftime('%Y-%m-%d %H:%M')}"


class Reserva(models.Model):
    """
    Modelo que representa la asistencia de un Deportista a una ClaseBJJ.
    """
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
        return f"Reserva: {self.deportista} -> {self.clase.titulo}"
