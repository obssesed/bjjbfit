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
