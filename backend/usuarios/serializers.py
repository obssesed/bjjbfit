from rest_framework import serializers
from .models import Deportista

class DeportistaSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Deportista.
    Transforma la instancia del modelo en JSON para su consumo por el Frontend (En este caso, Angular).
    """
    class Meta:
        model = Deportista
        fields = ['id', 'username', 'email', 'cinturon', 'telefono']
