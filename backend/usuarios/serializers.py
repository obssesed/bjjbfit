from rest_framework import serializers
from .models import Deportista

class DeportistaSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Deportista.
    Maneja la representación de datos y la creación segura de nuevos usuarios.
    """
    class Meta:
        model = Deportista
        fields = ['id', 'username', 'email', 'password', 'cinturon', 'telefono']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """
        Crea un nuevo Deportista utilizando el método create_user de Django 
        para asegurar que la contraseña se guarde de forma cifrada (hashing).
        """
        user = Deportista.objects.create_user(**validated_data)
        return user
