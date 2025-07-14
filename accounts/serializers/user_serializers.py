from rest_framework import serializers
from ..models import Usuario, Rol
from core.models import Empresa

class UsuarioRegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = ['empresa', 'rol', 'username', 'email', 'password']

    def validate_email(self, value):
        # Validar que el email no esté registrado
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("El correo ya está registrado.")
        return value

    def validate_username(self, value):
        # Validar que el username sea único
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("El nombre de usuario ya está en uso.")
        return value

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        exclude = ['password']


class UsuarioDetailSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)

    class Meta:
        model = Usuario
        exclude = ['password']
        read_only_fields = ['id', 'fecha_creacion', 'empresa_nombre', 'rol_nombre']


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    rol = serializers.PrimaryKeyRelatedField(queryset=Rol.objects.all(), required=False)

    class Meta:
        model = Usuario
        fields = ['rol', 'username', 'email', 'password']

    def validate_email(self, value):
        # Evitar duplicados al crear usuarios
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("El correo ya está registrado.")
        return value

    def validate_username(self, value):
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("El nombre de usuario ya está en uso.")
        return value

    def validate(self, data):
        user = self.context['request'].user

        # Solo superusuarios pueden asignar rol manualmente
        if not user.is_superuser and data.get('rol'):
            raise serializers.ValidationError("No tienes permiso para asignar un rol manualmente.")

        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        request_user = self.context['request'].user

        # Solo superusuarios pueden asignar empresa en validated_data (aunque no está en fields)
        empresa = request_user.empresa if not request_user.is_superuser else validated_data.get('empresa', None)

        user = Usuario(**validated_data)
        user.empresa = empresa
        user.set_password(password)
        user.save()
        return user

# from rest_framework import serializers
# from ..models import Usuario, Rol
# from core.models import Empresa

# class UsuarioRegistroSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = Usuario
#         fields = ['empresa', 'rol', 'username', 'email', 'password']

#     def create(self, validated_data):
#         return Usuario.objects.create_user(**validated_data)


# class UsuarioSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Usuario
#         exclude = ['password']




# class UsuarioDetailSerializer(serializers.ModelSerializer):  # mejor nombre estándar
#     empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
#     rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)

#     class Meta:
#         model = Usuario
#         exclude = ['password']
#         read_only_fields = ['id', 'fecha_creacion', 'empresa_nombre', 'rol_nombre']

# class UsuarioCreateSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=8)
#     rol = serializers.PrimaryKeyRelatedField(queryset=Rol.objects.all(), required=False)

#     class Meta:
#         model = Usuario
#         fields = ['rol', 'username', 'email', 'password']

#     def validate(self, data):
#         user = self.context['request'].user

#         # Solo superusuarios pueden asignar rol manualmente
#         if not user.is_superuser and data.get('rol'):
#             raise serializers.ValidationError("No tienes permiso para asignar un rol manualmente.")

#         return data

#     def create(self, validated_data):
#         password = validated_data.pop('password')
#         request_user = self.context['request'].user

#         # Solo superusuarios pueden asignar empresa en validated_data (aunque no está en fields)
#         empresa = request_user.empresa if not request_user.is_superuser else validated_data.get('empresa', None)

#         user = Usuario(**validated_data)
#         user.empresa = empresa
#         user.set_password(password)
#         user.save()
#         return user