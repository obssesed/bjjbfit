import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from usuarios.models import Deportista

def fix_admin():
    try:
        user = Deportista.objects.get(username='admin_bjj')
        user.set_password('Bjjbfit2026!')
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print("admin_bjj updated with password: Bjjbfit2026!")
    except Deportista.DoesNotExist:
        Deportista.objects.create_superuser(
            username='admin_bjj',
            email='admin_bjj@bjjbfit.com',
            password='Bjjbfit2026!'
        )
        print("admin_bjj created with password: Bjjbfit2026!")

if __name__ == "__main__":
    fix_admin()
