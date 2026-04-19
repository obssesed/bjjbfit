from django.contrib import admin
from django.contrib import messages
from .models import ClaseBJJ, Reserva
import datetime

import calendar

@admin.action(description="Replicar esta clase para el resto del mes")
def replicar_para_el_mes(modeladmin, request, queryset):
    clases_creadas = 0
    for clase in queryset:
        fecha_original = clase.fecha_hora_inicio
        # Calcular los días restantes en el mes para el mismo día de la semana
        ultimo_dia_mes = calendar.monthrange(fecha_original.year, fecha_original.month)[1]
        
        dia_siguiente = fecha_original + datetime.timedelta(days=7)
        while dia_siguiente.month == fecha_original.month and dia_siguiente.day <= ultimo_dia_mes:
            # Crear la réplica exacta pero en la semana siguiente
            ClaseBJJ.objects.create(
                titulo=clase.titulo,
                capacidad_maxima=clase.capacidad_maxima,
                fecha_hora_inicio=dia_siguiente
            )
            clases_creadas += 1
            dia_siguiente += datetime.timedelta(days=7)
            
    modeladmin.message_user(
        request, 
        f"Éxito: Se crearon {clases_creadas} nuevas sesiones para el resto del mes.", 
        messages.SUCCESS
    )

class ClaseBJJAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_hora_inicio', 'capacidad_maxima', 'plazas_disponibles')
    list_filter = ('fecha_hora_inicio',)
    actions = [replicar_para_el_mes]

admin.site.register(ClaseBJJ, ClaseBJJAdmin)
admin.site.register(Reserva)
