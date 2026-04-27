from rest_framework import serializers
from usuarios.models import Deportista
from .models import ClaseBJJ, Reserva

class ClaseBJJSerializer(serializers.ModelSerializer):
    """
    Serializador para ClaseBJJ.
    Incluye el campo calculado "plazas_disponibles" llamando a la lógica de negocio del modelo.
    """
    plazas_disponibles = serializers.SerializerMethodField()

    class Meta:
        model = ClaseBJJ
        fields = ['id', 'titulo', 'descripcion', 'fecha_hora_inicio', 'fecha_hora_fin', 'capacidad_maxima', 'plazas_disponibles']

    def get_plazas_disponibles(self, obj: ClaseBJJ) -> int:
        """
        Obtiene el número de plazas disponibles usando el método del "Fat Model".
        
        Args:
            obj (ClaseBJJ): La instancia de la clase actual.
        Returns:
            int: Cantidad de plazas libres.
        """
        return obj.plazas_disponibles()

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

        # 2. Aseguramos uniqueness manual (no pueden reservar la misma clase dos veces)
        clase = data.get('clase')
        if clase and Reserva.objects.filter(clase=clase, deportista=deportista_target, estado__in=['CONFIRMADA', 'ESPERA']).exists():
            raise serializers.ValidationError(
                "El deportista ya tiene una reserva activa para esta clase."
            )

        # 3. Restricciones Cronológicas
        from django.utils import timezone
        if clase and clase.fecha_hora_inicio < timezone.now():
            raise serializers.ValidationError(
                "No puedes reservar una clase que ya ha comenzado o finalizado."
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
