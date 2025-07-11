from rest_framework import serializers
from django.contrib.auth import authenticate
from ..models import Usuario

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError("Usuario y contraseña son obligatorios.")

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError("Credenciales inválidas.")

        if not user.activo:
            raise serializers.ValidationError("La cuenta está inactiva. Contacta al administrador.")

        data['user'] = user
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(min_length=8)
