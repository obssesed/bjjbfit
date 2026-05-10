from django.db import models
from django.contrib.auth.models import AbstractUser

class Plan(models.Model):
    """
    Modelo para gestionar los planes mensuales dinámicamente.
    """
    CATEGORIAS_EDAD = [
        ('ADULTO', 'Adulto (18+)'),
        ('JUVENIL', 'Juvenil (14-17)'),
        ('INFANTIL', 'Infantil (<14)'),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    precio_base = models.DecimalField(max_digits=6, decimal_places=2, help_text="Precio mensual normal")
    beneficios = models.TextField(help_text="Lista de beneficios separados por comas o saltos de línea")
    categoria_edad = models.CharField(max_length=20, choices=CATEGORIAS_EDAD, default='ADULTO')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.precio_base}€"

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Planes"


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
    metodo_pago = models.CharField(
        max_length=20,
        choices=[('EFECTIVO', 'Efectivo'), ('CUENTA', 'Cuenta')],
        default='EFECTIVO',
        help_text="Método de pago preferente del deportista."
    )
    
    # --- Membresías y Roles ---
    plan_activo = models.BooleanField(
        default=False,
        help_text="El admin activa manualmente el plan. Sin esto a True, no puede reservar."
    )
    tipo_plan = models.ForeignKey(
        Plan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios',
        help_text="Plan mensual asignado al deportista."
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
    
    # --- Seguridad ---
    requiere_cambio_password = models.BooleanField(
        default=False,
        help_text="Fuerza al usuario a cambiar su contraseña al hacer login."
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

class SolicitudReseteoPassword(models.Model):
    """
    Modelo para gestionar las solicitudes de reseteo de contraseña sin email.
    """
    usuario = models.ForeignKey(
        'Deportista', 
        on_delete=models.CASCADE,
        related_name='solicitudes_reseteo'
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    resuelta = models.BooleanField(default=False)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Solicitud de Reseteo"
        verbose_name_plural = "Solicitudes de Reseteo"
        ordering = ['-fecha_solicitud']

    def __str__(self):
        estado = "Resuelta" if self.resuelta else "Pendiente"
        return f"Solicitud de {self.usuario.username} - {estado}"

class Notificacion(models.Model):
    """
    Modelo para notificaciones internas.
    Pueden ser dirigidas a un usuario concreto o globales (para todos).
    """
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    es_global = models.BooleanField(default=False)
    destinatario = models.ForeignKey(
        'Deportista', 
        on_delete=models.CASCADE, 
        related_name='notificaciones_personales',
        null=True, 
        blank=True,
        help_text="Si está vacío y es_global es True, llega a todos."
    )
    leida = models.BooleanField(default=False, help_text="Solo aplica para notificaciones personales.")
    leida_por = models.ManyToManyField(
        'Deportista', 
        related_name='notificaciones_globales_leidas',
        blank=True,
        help_text="Track de quién ha leído la notificación global."
    )

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha_creacion']

    def __str__(self):
        tipo = "Global" if self.es_global else f"Para {self.destinatario.username if self.destinatario else '?'}"
        return f"{tipo}: {self.titulo}"
