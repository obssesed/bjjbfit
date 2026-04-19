from rest_framework import serializers
from .models import ClaseBJJ, Reserva

class ClaseBJJSerializer(serializers.ModelSerializer):
    """
    Serializador para ClaseBJJ.
    Incluye el campo calculado "plazas_disponibles" llamando a la lógica de negocio del modelo.
    """
    plazas_disponibles = serializers.SerializerMethodField()

    class Meta:
        model = ClaseBJJ
        fields = ['id', 'titulo', 'fecha_hora_inicio', 'capacidad_maxima', 'plazas_disponibles']

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
    class Meta:
        model = Reserva
        fields = ['id', 'clase', 'deportista', 'fecha_reserva']
        read_only_fields = ['deportista']

    def validate(self, data):
        """
        Validación a nivel de objeto para asegurar que la clase tiene cupo.
        """
        clase = data.get('clase')
        if clase and clase.plazas_disponibles() <= 0:
            raise serializers.ValidationError(
                "Lo sentimos, esta clase ya ha alcanzado su capacidad máxima."
            )
        return data

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
        return response
