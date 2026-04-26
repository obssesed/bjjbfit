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

    # --- Nuevos Campos (Reglas de Negocio BJJBFIT) ---
    nif = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="DNI/NIF. Los menores usan el de sus padres (puede haber duplicados por familia)."
    )
    id_interno = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="ID interno (modificable) asignado por el club."
    )
    fecha_nacimiento = models.DateField(
        null=True,
        blank=True,
        help_text="Útil para determinar automáticamente si es Adulto, Juvenil o Niño."
    )
    sexo = models.CharField(
        max_length=1,
        choices=[('M', 'Masculino'), ('F', 'Femenino')],
        blank=True,
        null=True
    )
    grados = models.PositiveSmallIntegerField(
        default=0,
        help_text="Grados en el cinturón del atleta (solo lo ve el admin)."
    )
    cuenta_bancaria = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="IBAN o cuenta (solo lo ve el admin)."
    )
    
    # --- Membresías y Roles ---
    plan_activo = models.BooleanField(
        default=False,
        help_text="El admin activa manualmente el plan. Sin esto a True, no puede reservar."
    )
    tipo_plan = models.CharField(
        max_length=50,
        choices=[('MENSUAL', 'Mensual'), ('FAMILIAR', 'Familiar')],
        null=True,
        blank=True
    )
    
    # --- Relación Familiar (1:N) ---
    padre_tutor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hijos_a_cargo',
        help_text="Relación Adulto -> Niños. Determina quién administra el perfil de un menor."
    )

    def __str__(self) -> str:
        """
        Retorna la representación inicial del deportista.
        """
        return f"{self.username} - {self.cinturon or 'Cinturón blanco sin grados'}"
