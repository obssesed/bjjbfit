from django.db import models
from usuarios.models import Deportista

class ClaseBJJ(models.Model):
    """
    Modelo que representa una sesión o clase de BJJ disponible en el gimnasio.
    """
    CHOICES_CATEGORIA = [
        ('ADULTO', 'Solo Adultos'),
        ('JUVENIL', 'Solo Juveniles'),
        ('INFANTIL', 'Solo Infantiles'),
    ]
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
        blank=True,
        null=True,
        help_text="Icono visual opcional (emoji)."
    )
    imagen_icono = models.FileField(
        upload_to='iconos_clases/',
        null=True,
        blank=True,
        help_text="Imagen personalizada para la clase."
    )
    categoria_acceso = models.CharField(
        max_length=20,
        choices=CHOICES_CATEGORIA,
        default='ADULTO',
        help_text="Qué tipo de plan se requiere para esta clase."
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
    icono = models.CharField(max_length=50, blank=True, null=True)
    imagen_icono = models.FileField(
        upload_to='iconos_clases/',
        null=True,
        blank=True,
        help_text="Imagen personalizada para la plantilla."
    )
    hora_inicio = models.TimeField(help_text="Hora de comienzo por defecto.")
    duracion_minutos = models.PositiveIntegerField(default=90)
    capacidad_maxima = models.PositiveIntegerField(default=30)
    categoria_acceso = models.CharField(
        max_length=20,
        choices=ClaseBJJ.CHOICES_CATEGORIA,
        default='ADULTO'
    )

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


class Actividad(models.Model):
    """
    Modelo para gestionar las actividades/servicios que se muestran en la Home.
    Permite al admin añadir, editar o eliminar servicios dinámicamente.
    """
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    badge = models.CharField(max_length=50, help_text="Etiqueta superior (ej: TÉCNICA, INTENSO).")
    imagen = models.FileField(
        upload_to='actividades/',
        null=True,
        blank=True,
        help_text="Imagen de fondo para la tarjeta."
    )
    orden = models.PositiveIntegerField(default=0, help_text="Orden de aparición en la web.")

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        ordering = ['orden', 'id']

    def __str__(self):
        return self.titulo


class Producto(models.Model):
    """
    Modelo para gestionar los productos de la tienda de la academia.
    """
    CHOICES_STOCK = [
        ('IN_STOCK', 'En Stock'),
        ('LOW_STOCK', 'Últimas tallas'),
        ('OUT_OF_STOCK', 'Agotado'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    tallas = models.CharField(max_length=100, help_text="Ej: A0, A1, A2 o S, M, L", blank=True, null=True)
    estado_stock = models.CharField(max_length=20, choices=CHOICES_STOCK, default='IN_STOCK')
    imagen = models.FileField(
        upload_to='productos/',
        null=True,
        blank=True,
        help_text="Imagen del producto."
    )
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['orden', 'id']

    def __str__(self):
        return self.nombre


class VideoRepaso(models.Model):
    """
    Modelo para los vídeos de repaso semanales.
    """
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    fecha_publicacion = models.DateField(auto_now_add=True)
    archivo_video = models.FileField(
        upload_to='videos/',
        help_text="Archivo de vídeo (mp4, webm, etc.)"
    )
    miniatura = models.ImageField(
        upload_to='videos/thumbnails/',
        null=True,
        blank=True,
        help_text="Imagen de previsualización para el vídeo."
    )
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Vídeo de Repaso"
        verbose_name_plural = "Vídeos de Repaso"
        ordering = ['-fecha_publicacion', 'orden', 'id']

    def __str__(self):
        return self.titulo
