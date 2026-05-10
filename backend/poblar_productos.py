import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from reservas.models import Producto

productos = [
    {
        "nombre": "Kimono Oficial BJJ Fit",
        "descripcion": "Kimono de alta calidad para competición y entrenamiento diario.",
        "tallas": "A0 · A1 · A2 · A3 · A4",
        "estado_stock": "IN_STOCK",
        "orden": 1
    },
    {
        "nombre": "Rashguard Academy",
        "descripcion": "Rashguard compresiva de secado rápido con diseño exclusivo.",
        "tallas": "S · M · L · XL",
        "estado_stock": "LOW_STOCK",
        "orden": 2
    },
    {
        "nombre": "Cinturones",
        "descripcion": "Cinturones oficiales de todos los colores y niveles.",
        "tallas": "Todos los niveles",
        "estado_stock": "IN_STOCK",
        "orden": 3
    },
    {
        "nombre": "Shorts Competición",
        "descripcion": "Shorts ultra ligeros y resistentes para No-Gi.",
        "tallas": "S · M · L · XL",
        "estado_stock": "IN_STOCK",
        "orden": 4
    }
]

for p in productos:
    Producto.objects.get_or_create(
        nombre=p['nombre'],
        defaults={
            "descripcion": p['descripcion'],
            "tallas": p['tallas'],
            "estado_stock": p['estado_stock'],
            "orden": p['orden']
        }
    )

print("Productos iniciales creados.")
