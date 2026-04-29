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
    OPCIONES_CINTURON = [
        # Adultos
        ('Blanco', 'Blanco'),
        ('Azul', 'Azul'),
        ('Morado', 'Morado'),
        ('Marrón', 'Marrón'),
        ('Negro', 'Negro'),
        # Infantiles
        ('Gris', 'Gris'),
        ('Amarillo', 'Amarillo'),
        ('Naranja', 'Naranja'),
        ('Verde', 'Verde'),
    ]

    cinturon = models.CharField(
        max_length=50, 
        choices=OPCIONES_CINTURON,
        default='Blanco',
        help_text="Grado o cinturón actual del deportista."
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
        help_text="Grados en el cinturón del atleta (0 a 4)."
    )
    fecha_ultima_graduacion = models.DateField(
        null=True,
        blank=True,
        help_text="Auto-fecha. Se actualiza sola si el profesor cambia el cinturón o los grados."
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
        choices=[
            ('ADULTO', 'Mensual Adulto'),
            ('JUVENIL', 'Mensual Juvenil'),
            ('INFANTIL', 'Mensual Infantil'),
        ],
        null=True,
        blank=True,
        help_text="Categoría del plan mensual según la edad del deportista."
    )
    es_familiar = models.BooleanField(
        default=False,
        help_text="Si es True, el deportista tiene un plan Familiar (descuento del 50%% para ambos familiares)."
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_cinturon = self.cinturon
        self._original_grados = getattr(self, 'grados', 0)

    def save(self, *args, **kwargs):
        from django.utils import timezone
        # Detectamos si es una actualización (pk exists) y si los grados o el color han cambiado
        if self.pk:
            if self.cinturon != self._original_cinturon or self.grados != self._original_grados:
                self.fecha_ultima_graduacion = timezone.now().date()
        else:
            # Si es nuevo, la fecha de graduacion inicial es hoy
            if not self.fecha_ultima_graduacion:
                self.fecha_ultima_graduacion = timezone.now().date()

        super().save(*args, **kwargs)
        # Actualizamos el estado interno en memoria por si se llama a save multiples veces
        self._original_cinturon = self.cinturon
        self._original_grados = self.grados

    def __str__(self) -> str:
        """
        Retorna la representación inicial del deportista.
        """
        return f"{self.username} - {self.cinturon or 'Cinturón blanco sin grados'}"
