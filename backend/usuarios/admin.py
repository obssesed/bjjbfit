from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Deportista

@admin.register(Deportista)
class DeportistaAdmin(UserAdmin):
    list_display = ('username', 'email', 'cinturon', 'grados', 'fecha_ultima_graduacion', 'plan_activo', 'padre_tutor')
    list_filter = ('cinturon', 'plan_activo')
    fieldsets = UserAdmin.fieldsets + (
        ('Datos BJJFIT', {
            'fields': ('nif', 'id_interno', 'fecha_nacimiento', 'sexo', 'cinturon', 'grados', 'fecha_ultima_graduacion', 'plan_activo', 'tipo_plan', 'padre_tutor', 'cuenta_bancaria', 'telefono')
        }),
    )
    readonly_fields = ('fecha_ultima_graduacion',)
