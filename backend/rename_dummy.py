import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from usuarios.models import Deportista

def renombrar():
    # Renombrar los usuarios que dicen "Nuevo" "Pupilo X"
    pendientes = Deportista.objects.filter(first_name="Nuevo", last_name__startswith="Pupilo")
    for p in pendientes:
        p.first_name = "Nueva"
        # Mantener el ID o numero si lo tuviera, pero el usuario dijo "pon Nueva alta"
        p.last_name = "alta"
        p.save()
        
    print("Usuarios renombrados a 'Nueva alta'.")

if __name__ == "__main__":
    renombrar()
