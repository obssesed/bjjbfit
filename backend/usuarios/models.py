from django.db import models
from django.contrib.auth.models import AbstractUser

class Deportista(AbstractUser):
    """
    Modelo que representa a un usuario o cliente del gimnasio de BJJ.
    Hereda de AbstractUser para extender la funcionalidad base de Django.
    """
    email = models.EmailField(
        unique=True,
        help_text="Correo electrónico de contacto y recepción de notificaciones."
    )
    cinturon = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Grado o cinturón actual del deportista (ej. Blanco, Azul, Morado)."
    )
    telefono = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Teléfono de contacto para emergencias o avisos."
    )

    def __str__(self) -> str:
        """
        Retorna la representación inicial del deportista.
        """
        return f"{self.username} - {self.cinturon or 'Cinturón blanco sin grados'}"
