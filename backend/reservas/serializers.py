from rest_framework import serializers
from usuarios.models import Deportista
from .models import ClaseBJJ, Reserva, PlantillaClase

class ClaseBJJSerializer(serializers.ModelSerializer):
    """
    Serializador para ClaseBJJ.
    Incluye el campo calculado "plazas_disponibles" llamando a la lógica de negocio del modelo.
    """
    plazas_disponibles = serializers.SerializerMethodField()
    plazas_ocupadas = serializers.SerializerMethodField()
    en_espera = serializers.SerializerMethodField()

    class Meta:
        model = ClaseBJJ
        fields = ['id', 'titulo', 'descripcion', 'icono', 'imagen_icono', 'categoria_acceso', 'fecha_hora_inicio', 'fecha_hora_fin', 'capacidad_maxima', 'plazas_disponibles', 'plazas_ocupadas', 'en_espera']

    def get_plazas_disponibles(self, obj: ClaseBJJ) -> int:
        return obj.plazas_disponibles()

    def get_plazas_ocupadas(self, obj: ClaseBJJ) -> int:
        return obj.plazas_ocupadas()
        
    def get_en_espera(self, obj: ClaseBJJ) -> int:
        return obj.en_espera()

    def validate(self, data):
        # Validar que no se cree otra clase igual (mismo título) en la misma fecha_hora_inicio
        titulo = data.get('titulo')
        fecha_hora_inicio = data.get('fecha_hora_inicio')

        if titulo and fecha_hora_inicio:
            query = ClaseBJJ.objects.filter(titulo=titulo, fecha_hora_inicio=fecha_hora_inicio)
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                raise serializers.ValidationError(
                    "Ya existe una clase de este tipo programada exactamente a la misma hora."
                )

        return data

class PlantillaClaseSerializer(serializers.ModelSerializer):
    categoria_acceso_display = serializers.CharField(source='get_categoria_acceso_display', read_only=True)
    class Meta:
        model = PlantillaClase
        fields = ['id', 'titulo', 'descripcion', 'icono', 'imagen_icono', 'hora_inicio', 'duracion_minutos', 'capacidad_maxima', 'categoria_acceso', 'categoria_acceso_display']

class ReservaSerializer(serializers.ModelSerializer):
    """
    Serializador para las Reservas generadas.
    """
    deportista = serializers.PrimaryKeyRelatedField(
        queryset=Deportista.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Reserva
        fields = ['id', 'clase', 'deportista', 'estado', 'fecha_reserva']
        validators = [] # Evita que DRF nos fuerce a mandar `deportista` por culpa del unique_together

    def validate(self, data):
        """
        Validación a nivel de objeto para reglas de negocio MVP.
        """
        request = self.context.get('request')
        user = request.user if request else None

        # 1. El usuario solicitante (Admin o normal) debe tener el plan activo? 
        # La regla dice "Plan debe estar activado por admin". 
        # Si envían un 'deportista' específico (ej. un hijo), miramos el plan_activo del deportista que recibe la clase.
        deportista_target = data.get('deportista', user)
        if not deportista_target.plan_activo:
            raise serializers.ValidationError(
                f"El deportista {deportista_target.username} no tiene un plan activo. Contacte con administración."
            )

        # 2. Aseguramos que el plan coincida con la categoría de la clase
        clase = data.get('clase')
        if clase and deportista_target.tipo_plan:
            if deportista_target.tipo_plan.categoria_edad != clase.categoria_acceso:
                raise serializers.ValidationError(
                    f"Esta clase es para la categoría {clase.get_categoria_acceso_display()}. "
                    f"Tu plan es de categoría {deportista_target.tipo_plan.get_categoria_edad_display()}."
                )

        # 3. Aseguramos uniqueness manual (no pueden reservar la misma clase dos veces)
        if clase and Reserva.objects.filter(clase=clase, deportista=deportista_target, estado__in=['CONFIRMADA', 'ESPERA']).exists():
            raise serializers.ValidationError(
                "El deportista ya tiene una reserva activa para esta clase."
            )

        # 3. Restricciones Cronológicas
        from django.utils import timezone
        import datetime
        now = timezone.now()
        
        if clase and clase.fecha_hora_inicio < now:
            raise serializers.ValidationError(
                "No puedes reservar una clase que ya ha comenzado o finalizado."
            )
            
        if clase and (clase.fecha_hora_inicio - now > datetime.timedelta(hours=24)):
            raise serializers.ValidationError(
                "Las reservas solo se abren con 24 horas de antelación al inicio de la clase."
            )

        # 4. Gestión de Aforo y Lista de Espera Automática
        if clase:
            if clase.plazas_disponibles() <= 0:
                # Si no hay hueco, sobreescribimos el estado mandado por el usuario (si lo hubo) a ESPERA.
                data['estado'] = 'ESPERA'
            else:
                data['estado'] = 'CONFIRMADA'
                
        return data

    def create(self, validated_data):
        from django.utils import timezone
        
        # Si el usuario había cancelado antes en esta misma clase, reaprovechamos
        # su registro para no violar el Meta.unique_together de Django en PostgreSQL.
        clase = validated_data.get('clase')
        deportista = validated_data.get('deportista')
        estado = validated_data.get('estado', 'CONFIRMADA')
        
        reserva, created = Reserva.objects.update_or_create(
            clase=clase, 
            deportista=deportista,
            defaults={'estado': estado, 'fecha_reserva': timezone.now()}
        )
        return reserva

    def to_representation(self, instance):
        """
        Sobrescribimos este método para que, aunque el cliente nos mande sólo el ID de la clase en el POST (Ej: clase: 2),
        cuando Django devuelva los datos de la reserva, incluya detalles útiles de la clase (como el título y fecha)
        para que la pantalla de 'Mi Perfil' de Angular pueda pintarlos.
        """
        response = super().to_representation(instance)
        response['clase_detalle'] = {
            'id': instance.clase.id,
            'titulo': instance.clase.titulo,
            'fecha_hora_inicio': instance.clase.fecha_hora_inicio
        }
        response['deportista_detalle'] = {
            'id': instance.deportista.id,
            'username': instance.deportista.username,
            'first_name': instance.deportista.first_name,
            'last_name': instance.deportista.last_name
        }
        return response
