from rest_framework import serializers
from .models import Deportista

class HijoSerializer(serializers.ModelSerializer):
    """
    Serializador muy leve para anidar en el Perfil del Padre
    """
    class Meta:
        model = Deportista
        fields = ['id', 'username', 'first_name', 'last_name', 'plan_activo', 'cinturon']

class DeportistaSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Deportista.
    Maneja la representación de datos y la creación segura de nuevos usuarios.
    """
    hijos_a_cargo = HijoSerializer(many=True, read_only=True)

    is_staff = serializers.BooleanField(read_only=True)

    class Meta:
        model = Deportista
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'cinturon', 'grados', 'fecha_ultima_graduacion', 'plan_activo', 'tipo_plan', 'es_familiar', 'telefono', 'nif', 'sexo', 'fecha_nacimiento', 'cuenta_bancaria', 'hijos_a_cargo', 'is_staff', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'nif': {'required': True, 'allow_blank': False},
            'sexo': {'required': True, 'allow_blank': False},
            'fecha_nacimiento': {'required': True},
            'plan_activo': {'read_only': True},
            'fecha_ultima_graduacion': {'read_only': True}
        }

    def create(self, validated_data):
        """
        Crea un nuevo Deportista utilizando el método create_user de Django 
        para asegurar que la contraseña se guarde de forma cifrada (hashing).
        """
        user = Deportista.objects.create_user(**validated_data)
        return user
