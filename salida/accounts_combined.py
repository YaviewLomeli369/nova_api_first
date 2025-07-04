
# --- /home/runner/workspace/accounts/__init__.py ---



# --- /home/runner/workspace/accounts/admin.py ---
from django.contrib import admin

# Register your models here.



# --- /home/runner/workspace/accounts/apps.py ---
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'



# --- /home/runner/workspace/accounts/tests.py ---
from django.test import TestCase

# Create your tests here.



# --- /home/runner/workspace/accounts/permissions.py ---



# --- /home/runner/workspace/accounts/urls.py ---
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import auth, profile, password_reset, mfa, audit
from accounts.views.roles import RolViewSet

router = DefaultRouter()
router.register(r'roles', RolViewSet)

urlpatterns = [
    path('login/', auth.LoginView.as_view()),
    path('logout/', auth.LogoutView.as_view()),
    path('register/', auth.RegisterView.as_view()),
    path('refresh/', auth.RefreshTokenView.as_view()),
    path('profile/', profile.ProfileView.as_view()),
    path('password-reset/request/', password_reset.PasswordResetRequestView.as_view()),
    path('password-reset/confirm/', password_reset.PasswordResetConfirmView.as_view()),
    path('2fa/enable/', mfa.EnableMFAView.as_view()),
    path('2fa/verify/', mfa.VerifyMFAView.as_view()),
    path('activity/', audit.ActivityLogView.as_view()),
    path('audit-log/', audit.AuditLogView.as_view()),
    path('', include(router.urls)),
]


# from django.urls import path
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
#     TokenVerifyView,
# )

# urlpatterns = [
#     path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
# ]



# --- /home/runner/workspace/accounts/models.py ---
# accounts/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from core.models import Empresa
from django.conf import settings

# accounts/models.py

from django.core.exceptions import ValidationError

class Auditoria(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name="auditorias")
    accion = models.CharField(max_length=255)
    tabla_afectada = models.CharField(max_length=255)
    registro_afectado = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Auditoría'
        verbose_name_plural = 'Auditorías'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.usuario} - {self.accion} ({self.timestamp})"

    def clean(self):
        """Validar antes de guardar."""
        if not self.usuario:
            raise ValidationError("El campo 'usuario' es obligatorio.")
        if not self.accion:
            raise ValidationError("El campo 'acción' es obligatorio.")
        if not self.tabla_afectada:
            raise ValidationError("El campo 'tabla_afectada' es obligatorio.")
        if not self.registro_afectado:
            raise ValidationError("El campo 'registro_afectado' es obligatorio.")



class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('El usuario debe tener un username')
        if not email:
            raise ValueError('El usuario debe tener un email válido')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('activo', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')
        return self.create_user(username, email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='usuarios')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    foto = models.URLField(blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    idioma = models.CharField(max_length=10, default='es')
    tema = models.CharField(max_length=50, default='claro')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UsuarioManager()

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']
        indexes = [
            models.Index(fields=['empresa', 'username']),
            models.Index(fields=['rol', 'activo']),
        ]

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username





# --- /home/runner/workspace/accounts/serializers.py ---
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Usuario, Rol, Auditoria
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


#PRUEBA
class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'  # O los campos específicos que quieras incluir


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['empresa', 'rol', 'username', 'email', 'password']

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)



# --- /home/runner/workspace/accounts/views/auth.py ---
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.serializers import LoginSerializer, UsuarioRegistroSerializer, UsuarioSerializer
from django.contrib.auth import authenticate

# Login básico
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UsuarioSerializer(user).data
        })

# Logout y revocación
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data['refresh'])
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# Registro de usuario
class RegisterView(generics.CreateAPIView):
    serializer_class = UsuarioRegistroSerializer
    permission_classes = [AllowAny]

# Refresh token (usamos TokenRefreshView de DRF SimpleJWT)
class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]



# --- /home/runner/workspace/accounts/views/profile.py ---
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from accounts.serializers import UsuarioSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user



# --- /home/runner/workspace/accounts/views/password_reset.py ---
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from accounts.models import Usuario

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = Usuario.objects.get(email=email)
            token = default_token_generator.make_token(user)
            reset_url = f"https://tusitio.com/reset-password/?token={token}"
            send_mail("Recupera tu contraseña", f"Enlace: {reset_url}", "no-reply@erp.com", [email])
            return Response({"msg": "Email enviado"}, status=200)
        except Usuario.DoesNotExist:
            return Response({"error": "Email no registrado"}, status=404)

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        # Aquí se puede verificar el token con algún sistema de validación (no implementado completo)
        return Response({"msg": "Contraseña cambiada correctamente"})



# --- /home/runner/workspace/accounts/views/mfa.py ---
import pyotp
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.serializers import EnableMFASerializer, VerifyMFASerializer

class EnableMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EnableMFASerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        method = serializer.validated_data['method']

        if method == "totp":
            secret = pyotp.random_base32()
            otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=request.user.email, issuer_name="Nova ERP")
            # Almacenar 'secret' en el modelo de usuario
            return Response({"secret": secret, "uri": otp_uri})
        # Enviar SMS (requiere integración con Twilio o similar)
        return Response({"msg": "Método SMS no implementado"}, status=status.HTTP_501_NOT_IMPLEMENTED)

class VerifyMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VerifyMFASerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        totp = pyotp.TOTP(request.user.profile.mfa_secret)
        if totp.verify(code):
            return Response({"msg": "MFA verificada"})
        return Response({"error": "Código inválido"}, status=400)



# --- /home/runner/workspace/accounts/views/roles.py ---
from rest_framework import viewsets
from accounts.models import Rol
from accounts.serializers import RolSerializer
from rest_framework.permissions import IsAuthenticated

class RolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]



# --- /home/runner/workspace/accounts/views/audit.py ---
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import Auditoria
from accounts.serializers import AuditoriaSerializer

class ActivityLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = Auditoria.objects.filter(usuario_id=request.user.id).order_by('-timestamp')[:50]
        data = AuditoriaSerializer(logs, many=True).data
        return Response(data)

class AuditLogView(APIView):
    permission_classes = [IsAuthenticated]  # ¿solo admins?

    def get(self, request):
        logs = Auditoria.objects.all().order_by('-timestamp')[:200]
        data = AuditoriaSerializer(logs, many=True).data
        return Response(data)



# --- /home/runner/workspace/accounts/views/__init__.py ---


