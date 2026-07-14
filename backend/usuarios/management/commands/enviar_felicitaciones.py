import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from usuarios.models import Deportista, Notificacion

class Command(BaseCommand):
    help = 'Envía notificaciones automáticas a los deportistas activos por su cumpleaños.'

    def handle(self, *args, **kwargs):
        hoy = timezone.now().date()
        
        deportistas = Deportista.objects.filter(
            is_active=True, 
            fecha_nacimiento__isnull=False,
            fecha_nacimiento__month=hoy.month,
            fecha_nacimiento__day=hoy.day
        )
        
        titulo = "¡Feliz Cumpleaños! 🎂"
        mensaje_base = "Desde el equipo de BJJBFIT te mandamos un abrazo inmenso y te deseamos un muy feliz cumpleaños. ¡Nos vemos en el tatami para celebrarlo! 🥳🥋"
        
        count = 0
        for dep in deportistas:
            # Comprobar si ya se le ha enviado hoy una notificación de cumpleaños
            ya_enviada = Notificacion.objects.filter(
                destinatario=dep,
                titulo=titulo,
                fecha_creacion__date=hoy
            ).exists()
            
            if not ya_enviada:
                Notificacion.objects.create(
                    titulo=titulo,
                    mensaje=mensaje_base,
                    es_global=False,
                    destinatario=dep,
                    leida=False
                )
                count += 1
                self.stdout.write(self.style.SUCCESS(f"Felicitación enviada a {dep.get_full_name() or dep.username}"))
        
        self.stdout.write(self.style.SUCCESS(f"Proceso finalizado. Se han enviado {count} notificaciones de cumpleaños hoy."))
