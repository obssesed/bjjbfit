import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from reservas.models import Actividad

actividades = [
    {
        "titulo": "BJJ con Gi",
        "descripcion": "La esencia del Jiu-Jitsu. Control posicional, palancas y estrangulaciones con kimono.",
        "badge": "TÉCNICA",
        "orden": 1
    },
    {
        "titulo": "No-Gi / Grappling",
        "descripcion": "Combate sin kimono. Enfoque en velocidad, wrestling y transiciones fluidas.",
        "badge": "DINÁMICO",
        "orden": 2
    },
    {
        "titulo": "BJJ Infantil",
        "descripcion": "Formación integral, disciplina y psicomotricidad para los futuros campeones.",
        "badge": "VALORES",
        "orden": 3
    },
    {
        "titulo": "Fit4Fight",
        "descripcion": "Entrenamiento funcional diseñado para maximizar tu rendimiento en el tatami.",
        "badge": "INTENSO",
        "orden": 4
    }
]

for a in actividades:
    Actividad.objects.get_or_create(
        titulo=a['titulo'],
        defaults={
            "descripcion": a['descripcion'],
            "badge": a['badge'],
            "orden": a['orden']
        }
    )

print("Actividades iniciales creadas.")
