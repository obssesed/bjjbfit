from rest_framework import serializers
from .models import Deportista, Plan, Notificacion, SolicitudReseteoPassword

class SolicitudReseteoPasswordSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username', read_only=True)
    first_name = serializers.CharField(source='usuario.first_name', read_only=True)
    last_name = serializers.CharField(source='usuario.last_name', read_only=True)

    class Meta:
        model = SolicitudReseteoPassword
        fields = ['id', 'username', 'first_name', 'last_name', 'fecha_solicitud', 'resuelta', 'fecha_resolucion']
        read_only_fields = ['fecha_solicitud', 'fecha_resolucion']

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = ['id', 'titulo', 'mensaje', 'fecha_creacion', 'es_global', 'destinatario', 'leida']

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'nombre', 'precio_base', 'beneficios', 'categoria_edad', 'activo']

class HijoSerializer(serializers.ModelSerializer):
    """
    Serializador para mostrar y permitir edición leve de hijos menores.
    """
    categoria_plan = serializers.SerializerMethodField()
    class Meta:
        model = Deportista
        fields = ['id', 'username', 'first_name', 'last_name', 'plan_activo', 'cinturon', 'categoria_plan', 'fecha_nacimiento', 'email', 'telefono', 'nif', 'sexo']

    def get_categoria_plan(self, obj):
        if obj.tipo_plan:
            return obj.tipo_plan.categoria_edad
        return None

class DeportistaSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Deportista.
    Maneja la representación de datos y la creación segura de nuevos usuarios.
    """
    hijos_a_cargo = serializers.SerializerMethodField()
    categoria_plan = serializers.SerializerMethodField()

    is_staff = serializers.BooleanField(read_only=True)

    class Meta:
        model = Deportista
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'cinturon', 'grados', 'fecha_ultima_graduacion', 'plan_activo', 'tipo_plan', 'categoria_plan', 'es_familiar', 'telefono', 'nif', 'sexo', 'fecha_nacimiento', 'cuenta_bancaria', 'metodo_pago', 'id_interno', 'hijos_a_cargo', 'is_staff', 'requiere_cambio_password', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
            'plan_activo': {'read_only': True},
            'fecha_ultima_graduacion': {'read_only': True},
            'tipo_plan': {'read_only': True},
            'es_familiar': {'read_only': True},
            'id_interno': {'read_only': True},
            'grados': {'read_only': True},
            'cinturon': {'read_only': True},
            'requiere_cambio_password': {'read_only': True},
        }

    def get_hijos_a_cargo(self, obj):
        """
        Devuelve solo los hijos que tienen menos de 14 años.
        """
        from datetime import date
        hoy = date.today()
        hijos_menores = []
        
        for hijo in obj.hijos_a_cargo.all():
            if hijo.fecha_nacimiento:
                edad = hoy.year - hijo.fecha_nacimiento.year - ((hoy.month, hoy.day) < (hijo.fecha_nacimiento.month, hijo.fecha_nacimiento.day))
                if edad < 14:
                    hijos_menores.append(hijo)
        
        return HijoSerializer(hijos_menores, many=True).data

    def get_categoria_plan(self, obj):
        if obj.tipo_plan:
            return obj.tipo_plan.categoria_edad
        return None

    def validate(self, attrs):
        """
        Validaciones personalizadas para proteger campos que solo el admin puede tocar.
        Si el usuario no es staff, quitamos del diccionario attrs cualquier intento
        de modificar nombre, apellidos, etc., para que el save() no los procese.
        """
        request = self.context.get('request')
        
        # Validación de campos obligatorios SOLO para registro (creación)
        if not self.instance:
            campos_obligatorios = ['first_name', 'last_name', 'nif', 'sexo', 'fecha_nacimiento']
            errors = {}
            for campo in campos_obligatorios:
                if not attrs.get(campo):
                    errors[campo] = "Este campo es obligatorio para el registro."
            if errors:
                raise serializers.ValidationError(errors)

        if self.instance and request and not request.user.is_staff:
            # Campos que el usuario común NO puede modificar nunca (solo en edición)
            attrs.pop('first_name', None)
            attrs.pop('last_name', None)
            attrs.pop('username', None)
        
        # Validación de cuenta bancaria si el método es CUENTA
        metodo_pago = attrs.get('metodo_pago')
        cuenta_bancaria = attrs.get('cuenta_bancaria')
        
        # Si metodo_pago viene en la peticion y es CUENTA, validamos cuenta_bancaria
        # Si no viene metodo_pago pero el usuario ya lo tiene como CUENTA en DB, también validamos si intenta vaciar cuenta_bancaria
        actual_metodo = getattr(request.user if request else None, 'metodo_pago', 'EFECTIVO')
        final_metodo = metodo_pago or actual_metodo
        
        if final_metodo == 'CUENTA':
            final_cuenta = cuenta_bancaria if cuenta_bancaria is not None else getattr(request.user if request else None, 'cuenta_bancaria', None)
            if not final_cuenta:
                raise serializers.ValidationError({"cuenta_bancaria": "Es obligatorio indicar una cuenta bancaria para el método de pago por cuenta."})

        return attrs

    def create(self, validated_data):
        """
        Crea un nuevo Deportista utilizando el método create_user de Django 
        para asegurar que la contraseña se guarde de forma cifrada (hashing).
        """
        user = Deportista.objects.create_user(**validated_data)
        return user
