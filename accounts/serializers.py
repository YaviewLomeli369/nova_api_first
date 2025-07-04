from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Usuario, Rol
from core.models import Empresa
import pyotp

# Serializer para Login
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Credenciales inválidas")
        if not user.activo:
            raise serializers.ValidationError("Cuenta inactiva")
        data['user'] = user
        return data

# Serializer para Registro
class UsuarioRegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['empresa', 'rol', 'username', 'email', 'password']

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)

# Serializer para perfil
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        exclude = ['password']

# MFA (TOTP)
class EnableMFASerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=["totp", "sms"])

class VerifyMFASerializer(serializers.Serializer):
    code = serializers.CharField()

# Password Reset
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField()

# Auditoría
# class AuditoriaSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     usuario_id = serializers.IntegerField()
#     accion = serializers.CharField()
#     tabla_afectada = serializers.CharField()
#     registro_afectado = serializers.CharField()
#     timestamp = serializers.DateTimeField()
class AuditoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auditoria
        fields = ['id', 'usuario', 'accion', 'tabla_afectada', 'registro_afectado', 'timestamp']
        read_only_fields = ['id', 'timestamp']  # No queremos que se pueda modificar el ID ni el timestamp
        extra_kwargs = {
            'accion': {'required': True},
            'tabla_afectada': {'required': True},
            'registro_afectado': {'required': True},
        }