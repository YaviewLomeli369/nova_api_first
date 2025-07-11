# from rest_framework import serializers
# from django.contrib.auth import authenticate
# from .models import Usuario, Rol, Auditoria
# from core.models import Empresa
# import pyotp
# # from accounts.serializers import AuditoriaSerializerMFALoginVerifyView
# # Serializer para Login
# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         username = data.get('username')
#         password = data.get('password')

#         if not username or not password:
#             raise serializers.ValidationError("Usuario y contraseña son obligatorios.")

#         user = authenticate(username=username, password=password)

#         if user is None:
#             raise serializers.ValidationError("Credenciales inválidas.")

#         if not user.activo:
#             raise serializers.ValidationError("La cuenta está inactiva. Contacta al administrador.")

#         data['user'] = user
#         return data

# # Serializer para Registro
# class UsuarioRegistroSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = Usuario
#         fields = ['empresa', 'rol', 'username', 'email', 'password']

#     def create(self, validated_data):
#         return Usuario.objects.create_user(**validated_data)

# # Serializer para perfil
# class UsuarioSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Usuario
#         exclude = ['password']

# # MFA (TOTP)
# class EnableMFASerializer(serializers.Serializer):
#     method = serializers.ChoiceField(choices=["totp", "sms"])

# class VerifyMFASerializer(serializers.Serializer):
#     code = serializers.CharField()

# # Password Reset
# class PasswordResetRequestSerializer(serializers.Serializer):
#     email = serializers.EmailField()

# class PasswordResetConfirmSerializer(serializers.Serializer):
#     uidb64 = serializers.CharField()  # nuevo
#     token = serializers.CharField()
#     password = serializers.CharField(min_length=8)




# class AuditoriaSerializer(serializers.ModelSerializer):
#     usuario = serializers.StringRelatedField()

#     class Meta:
#         model = Auditoria
#         fields = [
#             'id',
#             'usuario',
#             'accion',
#             'tabla_afectada',
#             'registro_afectado',
#             'timestamp',
#         ]


# #PRUEBA
# class RolSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Rol
#         fields = '__all__'



# # Serializer para crear usuario
# class UsuarioCreateSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=8)

#     class Meta:
#         model = Usuario
#         fields = ['empresa', 'rol', 'username', 'email', 'password']

#     def create(self, validated_data):
#         return Usuario.objects.create_user(**validated_data)

# # Serializer para listar, actualizar, eliminar usuario
# class UsuarioDetailSerializer(serializers.ModelSerializer):
#     empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
#     rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)

#     class Meta:
#         model = Usuario
#         exclude = ['password']
#         read_only_fields = ['id', 'fecha_creacion', 'empresa_nombre', 'rol_nombre']

# class MFAEnableSerializer(serializers.Serializer):
#     # En la activación solo se confirma que el usuario quiere activar
#     pass

# class MFAVerifySerializer(serializers.Serializer):
#     code = serializers.CharField(max_length=6)

# class MFADisableSerializer(serializers.Serializer):
#     code = serializers.CharField(max_length=6)