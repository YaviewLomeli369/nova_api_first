
# --- /home/runner/workspace/accounts/__init__.py ---



# --- /home/runner/workspace/accounts/tests.py ---
from django.test import TestCase

# Create your tests here.



# --- /home/runner/workspace/accounts/permissions.py ---
from rest_framework.permissions import BasePermission

class HasCustomPermission(BasePermission):
    def __init__(self, permiso):
        self.permiso = permiso

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_perm(self.permiso)


# --- /home/runner/workspace/accounts/signals.py ---
# accounts/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from accounts.models import Auditoria, Usuario
from django.conf import settings
import threading

# Hilo-local para almacenar temporalmente el usuario
_local = threading.local()

def set_audit_user(user):
    _local.user = user

def get_audit_user():
    return getattr(_local, 'user', None)


def registrar_auditoria(instance, accion):
    modelo = instance.__class__.__name__
    usuario = get_audit_user()
    if not usuario or not isinstance(usuario, Usuario):
        return

    Auditoria.objects.create(
        usuario=usuario,
        accion=accion,
        tabla_afectada=modelo,
        registro_afectado=str(instance)
    )

# --- Señales globales ---

@receiver(post_save)
def auditoria_crear_modificar(sender, instance, created, **kwargs):
    if sender._meta.app_label in ['accounts', 'ventas', 'compras', 'inventario']:
        accion = "CREADO" if created else "MODIFICADO"
        registrar_auditoria(instance, accion)

@receiver(post_delete)
def auditoria_eliminar(sender, instance, **kwargs):
    if sender._meta.app_label in ['accounts', 'ventas', 'compras', 'inventario']:
        registrar_auditoria(instance, "ELIMINADO")



# --- /home/runner/workspace/accounts/apps.py ---
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import accounts.signals  # 👈 conecta señales


# --- /home/runner/workspace/accounts/filters.py ---
# accounts/filters.py
import django_filters
from accounts.models import Auditoria

class AuditoriaFilter(django_filters.FilterSet):
    fecha_inicio = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    fecha_fin = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')

    class Meta:
        model = Auditoria
        fields = {
            'usuario__username': ['exact', 'icontains'],
            'accion': ['exact', 'icontains'],
            'tabla_afectada': ['exact', 'icontains'],
        }



# --- /home/runner/workspace/accounts/schema.py ---
# from drf_spectacular.utils import extend_schema_view, extend_schema

# @extend_schema_view(
#     post=extend_schema(summary="Login", description="Autenticación con JWT"),
#     get=extend_schema(summary="Ver perfil", description="Datos del usuario autenticado"),
# )
# class AuthViewSet(viewsets.ViewSet):
#     pass


# --- /home/runner/workspace/accounts/admin.py ---
# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import Usuario, Rol, Auditoria

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'empresa', 'rol')  # elimina is_staff, is_active
    list_filter = ('rol', 'empresa')  # elimina is_staff, is_active

    # Campos para el formulario de edición
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('email', 'empresa', 'rol')}),
        ('Permisos', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    # Campos que se usarán para crear usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'empresa', 'rol', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    search_fields = ('username', 'email')
    ordering = ('username',)

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    list_display = ('nombre', 'descripcion')


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'accion', 'tabla_afectada', 'timestamp')
    list_filter = ('accion', 'tabla_afectada', 'timestamp')
    search_fields = ('usuario__username', 'accion', 'tabla_afectada', 'registro_afectado')
    readonly_fields = ('usuario', 'accion', 'tabla_afectada', 'registro_afectado', 'timestamp')

    def has_add_permission(self, request):
        return False  # No se permite agregar registros manualmente

    def has_delete_permission(self, request, obj=None):
        return False  # Opcional: impedir borrar registros para mantener integridad


# --- /home/runner/workspace/accounts/models.py ---
# accounts/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from core.models import Empresa
from django.conf import settings


# accounts/models.py

from django.core.exceptions import ValidationError


from django.db import models

from django.core.exceptions import ValidationError
from django.db import models

class Auditoria(models.Model):
    usuario = models.ForeignKey(
        'Usuario', 
        null=True, blank=True,  # ← Permitir que sea opcional
        on_delete=models.SET_NULL,  # ← No eliminar auditorías si se borra el usuario
        related_name="auditorias"
    )
    username_intentado = models.CharField(
        max_length=150, 
        null=True, blank=True, 
        help_text="Nombre de usuario usado en caso de login fallido"
    )
    accion = models.CharField(max_length=255)
    tabla_afectada = models.CharField(max_length=255)
    registro_afectado = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Auditoría'
        verbose_name_plural = 'Auditorías'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.usuario or self.username_intentado} - {self.accion} ({self.timestamp})"

    def clean(self):
        if not self.usuario and not self.username_intentado:
            raise ValidationError("Debe proporcionarse 'usuario' o 'username_intentado'.")
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


from django.contrib.auth.models import BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, empresa=None, **extra_fields):
        if not empresa:
            raise ValueError("El campo empresa es obligatorio")
        if not username:
            raise ValueError('El usuario debe tener un nombre de usuario')
        email = self.normalize_email(email)

        # Aseguramos valores por defecto para los flags de estado
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('activo', True)  # Si usas este campo personalizado
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        user = self.model(
            username=username,
            email=email,
            empresa=empresa,
            **extra_fields  # Pasa todos los campos extra para asignarlos directo
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, empresa=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('activo', True)

        if empresa is None:
            raise ValueError("El superusuario debe tener una empresa asignada")

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(username, email, password, empresa=empresa, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='usuarios')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    # password = models.CharField(max_length=128)

    activo = models.BooleanField(default=True)  # si quieres mantenerlo aparte
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

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




# --- /home/runner/workspace/accounts/urls.py ---
# accounts/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importación de vistas por módulos
from accounts.views import auth, profile, password_reset, mfa, audit, users
from accounts.views.roles import RolViewSet
from accounts.views.users import UsuarioViewSet
from accounts.views.audit import AuditLogListView, AuditLogExportCSV
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views.mfa import MFAEnableView, MFAVerifyView, MFADisableView, MFALoginVerifyView

# Rutas registradas con router para vistas basadas en ViewSet
router = DefaultRouter()
router.register(r'users', UsuarioViewSet, basename='usuarios')
router.register(r'roles', RolViewSet)

# Lista de URLs explícitas
urlpatterns = [

    # --- Autenticación ---
    path('login/', auth.LoginView.as_view(), name='login'),                        # POST - Iniciar sesión
    path('logout/', auth.LogoutView.as_view(), name='logout'),                     # POST - Cerrar sesión
    path('register/', auth.RegisterView.as_view(), name='register'),               # POST - Registro de usuario
    path('refresh/', auth.RefreshTokenView.as_view(), name='token-refresh'),       # POST - Refrescar token JWT

    # --- Perfil de usuario ---
    path('profile/', profile.ProfileView.as_view(), name='profile'),               # GET/PUT - Ver o editar perfil

    # --- Recuperación de contraseña ---
    path('password-reset/request/', password_reset.PasswordResetRequestView.as_view(), name='password-reset-request'),  # POST - Solicitar reinicio
    path('password-reset/confirm/', password_reset.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),  # POST - Confirmar reinicio

    # --- Autenticación de dos factores (2FA) ---
    path('2fa/verify-login/', MFALoginVerifyView.as_view(), name='mfa-verify-login'),  # POST - Verificar 2FA en login
    path('2fa/enable/', MFAEnableView.as_view(), name='mfa-enable'),                   # POST - Habilitar 2FA
    path('2fa/verify/', MFAVerifyView.as_view(), name='mfa-verify'),                   # POST - Verificar código 2FA
    path('2fa/disable/', MFADisableView.as_view(), name='mfa-disable'),                # POST - Deshabilitar 2FA

    # --- Actividad del usuario ---
    path('activity/', audit.ActivityLogView.as_view(), name='activity-log'),                # GET - Ver actividad

    # --- Auditoría ---
    path('audit-log/', AuditLogListView.as_view(), name='audit-log-list'),                  # GET - Lista de logs de auditoría
    path('audit-log/export-csv/', AuditLogExportCSV.as_view(), name='audit-log-export-csv'),# GET - Exportar logs como CSV

    # --- Vistas registradas mediante router (ViewSets) ---
    path('', include(router.urls)),

    # --- Documentación (Swagger/OpenAPI) ---
    path('schema/', SpectacularAPIView.as_view(), name='schema'),                       # Esquema OpenAPI
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui') # UI de Swagger
]




# --- /home/runner/workspace/accounts/serializers.py ---
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Usuario, Rol, Auditoria
from core.models import Empresa
import pyotp
# from accounts.serializers import AuditoriaSerializerMFALoginVerifyView
# Serializer para Login
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
# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         user = authenticate(username=data['username'], password=data['password'])
#         if not user:
#             raise serializers.ValidationError("Credenciales inválidas")
#         if not user.activo:
#             raise serializers.ValidationError("Cuenta inactiva")
#         data['user'] = user
#         return data

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
    uidb64 = serializers.CharField()  # nuevo
    token = serializers.CharField()
    password = serializers.CharField(min_length=8)




class AuditoriaSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()

    class Meta:
        model = Auditoria
        fields = [
            'id',
            'usuario',
            'accion',
            'tabla_afectada',
            'registro_afectado',
            'timestamp',
        ]
        
# class AuditoriaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Auditoria
#         fields = ['id', 'usuario', 'accion', 'tabla_afectada', 'registro_afectado', 'timestamp']
#         read_only_fields = ['id', 'timestamp']  # No queremos que se pueda modificar el ID ni el timestamp
#         extra_kwargs = {
#             'accion': {'required': True},
#             'tabla_afectada': {'required': True},
#             'registro_afectado': {'required': True},
#         }


#PRUEBA
class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['empresa', 'rol', 'username', 'email', 'password']

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)

# Serializer para crear usuario
class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = ['empresa', 'rol', 'username', 'email', 'password']

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)

# Serializer para listar, actualizar, eliminar usuario
class UsuarioDetailSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)

    class Meta:
        model = Usuario
        exclude = ['password']
        read_only_fields = ['id', 'fecha_creacion', 'empresa_nombre', 'rol_nombre']

class MFAEnableSerializer(serializers.Serializer):
    # En la activación solo se confirma que el usuario quiere activar
    pass

class MFAVerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)

class MFADisableSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)


# --- /home/runner/workspace/accounts/views/profile.py ---
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from accounts.serializers import UsuarioSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user



# --- /home/runner/workspace/accounts/views/users.py ---
# accounts/views/users.py

from rest_framework import viewsets, permissions, filters
from accounts.models import Usuario
from accounts.serializers import UsuarioCreateSerializer, UsuarioDetailSerializer
from django_filters.rest_framework import DjangoFilterBackend

class UsuarioViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Usuario.objects.select_related('empresa', 'rol').all()
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['username', 'email']
    filterset_fields = ['activo', 'empresa', 'rol']

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioDetailSerializer

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save()



# --- /home/runner/workspace/accounts/views/__init__.py ---
from .auth import *
from .profile import *
from .password_reset import *
from .mfa import *
from .audit import *
from .users import UsuarioViewSet
from .roles import RolViewSet


# --- /home/runner/workspace/accounts/views/roles.py ---
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from accounts.models import Rol
from accounts.serializers import RolSerializer

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]


# --- /home/runner/workspace/accounts/views/password_reset.py ---
# accounts/views/password_reset.py

from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from accounts.models import Usuario
from accounts.utils.auditoria import registrar_auditoria

# ----------------------------------------
# 🔐 SERIALIZERS
# ----------------------------------------

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(min_length=8)
    code = serializers.CharField(required=False)  # Solo si tiene MFA


# ----------------------------------------
# 📤 SOLICITUD DE RECUPERACIÓN
# ----------------------------------------

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = Usuario.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            reset_url = f"https://tusitio.com/reset-password/?uidb64={uidb64}&token={token}"
            send_mail(
                subject="Recupera tu contraseña",
                message=f"Enlace para resetear: {reset_url}",
                from_email="no-reply@erp.com",
                recipient_list=[email],
                fail_silently=False,
            )
            return Response({"msg": "Email enviado"}, status=200)

        except Usuario.DoesNotExist:
            return Response({"error": "Email no registrado"}, status=404)


# ----------------------------------------
# ✅ CONFIRMACIÓN DEL CAMBIO DE CONTRASEÑA
# ----------------------------------------

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = serializer.validated_data['uidb64']
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        code = serializer.validated_data.get('code')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            return Response({"error": "Usuario inválido"}, status=400)

        if default_token_generator.check_token(user, token):
            if user.mfa_enabled:
                if not code:
                    return Response({"error": "Código MFA requerido"}, status=400)
                totp = pyotp.TOTP(user.mfa_secret)
                if not totp.verify(code):
                    registrar_auditoria(user, "RESET_MFA_FAIL", "Usuario", "Código MFA inválido")
                    return Response({"error": "Código MFA inválido"}, status=400)

            user.set_password(password)
            user.save()
            registrar_auditoria(user, "RESET_PASSWORD", "Usuario", "Contraseña restablecida con éxito")
            return Response({"msg": "Contraseña cambiada correctamente"})
        # if not default_token_generator.check_token(user, token):
        #     return Response({"error": "Token inválido o expirado"}, status=400)

        # if user.mfa_enabled:
        #     if not code:
        #         return Response({"error": "Código MFA requerido"}, status=400)

        #     totp = pyotp.TOTP(user.mfa_secret)
        #     if not totp.verify(code):
        #         return Response({"error": "Código MFA inválido"}, status=400)

        # user.set_password(password)
        # user.save()
        # return Response({"msg": "Contraseña cambiada correctamente"})

# class PasswordResetConfirmView(APIView):
#     def post(self, request):
#         serializer = PasswordResetConfirmSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         uidb64 = serializer.validated_data['uidb64']
#         token = serializer.validated_data['token']
#         password = serializer.validated_data['password']

#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = Usuario.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
#             return Response({"error": "Usuario inválido"}, status=400)

#         if default_token_generator.check_token(user, token):
#             user.set_password(password)
#             user.save()
#             return Response({"msg": "Contraseña cambiada correctamente"})
#         else:
#             return Response({"error": "Token inválido o expirado"}, status=400)



# --- /home/runner/workspace/accounts/views/auth.py ---
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.serializers import LoginSerializer, UsuarioRegistroSerializer, UsuarioSerializer
from accounts.utils.auditoria import registrar_auditoria
from rest_framework.decorators import action, permission_classes

from rest_framework.authentication import BaseAuthentication

class NoAuthentication(BaseAuthentication):
    def authenticate(self, request):
        return None



class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [NoAuthentication]  # 👈 Esto anula la validación del token
    def post(self, request):
        print("Headers recibidos:", request.headers)
        serializer = LoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            username = request.data.get("username", "desconocido")
            registrar_auditoria(
                usuario=None,
                username_intentado=username,
                accion="LOGIN_FAIL",
                tabla="Usuario",
                registro=f"Intento fallido de login para '{username}'"
            )
            raise

        user = serializer.validated_data['user']

        if getattr(user, 'mfa_enabled', False):
            temp_token = RefreshToken.for_user(user)
            registrar_auditoria(
                usuario=user,
                accion="LOGIN_MFA",
                tabla="Usuario",
                registro="Login exitoso (pendiente MFA)"
            )
            return Response({
                'mfa_required': True,
                'temp_token': str(temp_token.access_token),
                'detail': 'MFA_REQUIRED'
            }, status=202)

        refresh = RefreshToken.for_user(user)
        registrar_auditoria(
            usuario=user,
            accion="LOGIN",
            tabla="Usuario",
            registro="Login exitoso"
        )
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UsuarioSerializer(user).data
        })
        


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"detail": "Refresh token required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            registrar_auditoria(
                usuario=request.user,
                accion="LOGOUT",
                tabla="Usuario",
                registro="Logout exitoso"
            )
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            # Podés agregar logging aquí con e para debug
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    serializer_class = UsuarioRegistroSerializer
    permission_classes = [AllowAny]


class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]





# --- /home/runner/workspace/accounts/views/audit.py ---
# accounts/views/audit.py
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser
from rest_framework.pagination import PageNumberPagination
from accounts.models import Auditoria
from accounts.serializers import AuditoriaSerializer
from accounts.filters import AuditoriaFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import Auditoria
from accounts.serializers import AuditoriaSerializer
from django.http import HttpResponse
import csv

class AuditLogExportCSV(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Aplicar filtros con el mismo filtro set
        filtro = AuditoriaFilter(request.GET, queryset=Auditoria.objects.all())

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="audit_log.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Usuario', 'Acción', 'Tabla', 'Registro Afectado', 'Fecha/Hora'])

        for entry in filtro.qs.order_by('-timestamp'):
            writer.writerow([
                entry.id,
                str(entry.usuario),
                entry.accion,
                entry.tabla_afectada,
                entry.registro_afectado,
                entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        return response

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

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100

class AuditLogListView(generics.ListAPIView):
    queryset = Auditoria.objects.all()
    serializer_class = AuditoriaSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AuditoriaFilter
    ordering_fields = ['timestamp', 'usuario__username', 'accion', 'tabla_afectada']
    ordering = ['-timestamp']
    pagination_class = StandardResultsSetPagination


# --- /home/runner/workspace/accounts/views/mfa.py ---
# accounts/views/mfa.py

import pyotp
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from accounts.serializers import MFAEnableSerializer, MFAVerifySerializer, MFADisableSerializer
from rest_framework.permissions import AllowAny
from accounts.utils.auditoria import registrar_auditoria
from ..models import Usuario  # Asegúrate de que esta importación esté presente
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from datetime import timedelta

from rest_framework_simplejwt.tokens import AccessToken



def generate_temp_token(user):
    # Crear un AccessToken para el usuario
    access_token = AccessToken.for_user(user)
    # Aquí puedes agregar más datos si es necesario
    access_token.set_exp(lifetime=timedelta(minutes=5))  # Establecer un tiempo de expiración corto
    return str(access_token)

class MFAEnableView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.mfa_enabled:
            return Response({"detail": "MFA ya está activado."}, status=status.HTTP_400_BAD_REQUEST)

        # Generar nuevo secreto
        secret = pyotp.random_base32()
        user.mfa_secret = secret
        user.save()

        # Generar URL para QR (otpauth)
        otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.username, issuer_name="Nova ERP"
        )

        return Response({
            "otp_uri": otp_uri,
            "secret": secret,  # opcional mostrar clave manualmente
        })

class MFAVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = MFAVerifySerializer(data=request.data)

        # Verificar que los datos del serializer son válidos
        serializer.is_valid(raise_exception=True)

        # Obtener el código MFA del serializer
        code = serializer.validated_data['code']

        # Verificar si el usuario tiene configurado MFA
        if not user.mfa_secret:
            return Response(
                {"detail": "MFA no está configurado para este usuario."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generar el objeto TOTP y verificar el código
        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(code):
            # Si el código es válido, habilitar MFA para el usuario
            user.mfa_enabled = True
            user.save()

            # Registrar la auditoría para activación exitosa
            registrar_auditoria(user, "MFA_ACTIVADO", "Usuario", "MFA activado correctamente")

            return Response({"detail": "MFA activado correctamente."})
        else:
            # Registrar la auditoría para intento fallido
            registrar_auditoria(user, "MFA_FALLIDO", "Usuario", "Código MFA inválido")

            return Response(
                {"detail": "Código MFA inválido. Por favor, intente nuevamente."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

# class MFAVerifyView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         serializer = MFAVerifySerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         code = serializer.validated_data['code']
#         if not user.mfa_secret:
#             return Response({"detail": "MFA no está configurado."}, status=status.HTTP_400_BAD_REQUEST)

#         totp = pyotp.TOTP(user.mfa_secret)
#         if totp.verify(code):
#             user.mfa_enabled = True
#             user.save()
#             registrar_auditoria(user, "MFA_ACTIVADO", "Usuario", "MFA activado correctamente")
#             return Response({"detail": "MFA activado correctamente."})
#         else:
#             registrar_auditoria(user, "MFA_FALLIDO", "Usuario", "Código MFA inválido")
#             return Response({"detail": "Código inválido."}, status=400)
        # if totp.verify(code):
        #     user.mfa_enabled = True
        #     user.save()
        #     return Response({"detail": "MFA activado correctamente."})
        # else:
        #     return Response({"detail": "Código inválido."}, status=status.HTTP_400_BAD_REQUEST)

class MFADisableView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = MFADisableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']
        if not user.mfa_enabled:
            return Response({"detail": "MFA no está activado."}, status=status.HTTP_400_BAD_REQUEST)

        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(code):
            user.mfa_enabled = False
            user.mfa_secret = ""
            user.save()
            registrar_auditoria(user, "MFA_DESACTIVADO", "Usuario", "MFA desactivado")
            return Response({"detail": "MFA desactivado correctamente."})
        else:
            return Response({"detail": "Código inválido."}, status=status.HTTP_400_BAD_REQUEST)




class MFALoginVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("temp_token")  # El token temporal que el cliente recibe
        code = request.data.get("code")  # El código OTP del usuario

        # Validar datos incompletos
        if not token or not code:
            return Response({"detail": "Datos incompletos"}, status=400)

        try:
            # Decodificar el token temporal
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = Usuario.objects.get(id=user_id)
        except KeyError:
            return Response({"detail": "Token mal formado"}, status=400)
        except Usuario.DoesNotExist:
            return Response({"detail": "Usuario no encontrado"}, status=404)

        # Verificar si el usuario tiene habilitado 2FA
        if not user.mfa_secret:
            return Response({"detail": "2FA no habilitado para este usuario"}, status=400)

        # Verificar el código de 2FA
        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(code):
            # Si el código es válido, generar nuevos tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UsuarioSerializer(user).data
            })

        # Si el código 2FA es incorrecto
        return Response({"detail": "Código MFA inválido"}, status=400)



# class MFALoginVerifyView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         # Obtener datos de la solicitud
#         token = request.data.get("temp_token")
#         code = request.data.get("code")

#         # Verificar si los datos son completos
#         if not token or not code:
#             return Response({"detail": "Datos incompletos"}, status=400)

#         try:
#             # Verificar el token temporal
#             access_token = AccessToken(token)
#             user_id = access_token['user_id']
#             user = Usuario.objects.get(id=user_id)
#         except KeyError:
#             return Response({"detail": "Token mal formado"}, status=400)
#         except Usuario.DoesNotExist:
#             return Response({"detail": "Usuario no encontrado"}, status=404)

#         # Verificar si el usuario tiene habilitado MFA
#         if not user.mfa_secret:
#             return Response({"detail": "2FA no habilitado para este usuario"}, status=400)

#         # Verificar el código de 2FA
#         totp = pyotp.TOTP(user.mfa_secret)
#         if totp.verify(code):
#             # Si el código es válido, generar nuevos tokens
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 'access': str(refresh.access_token),
#                 'refresh': str(refresh),
#                 'user': UsuarioSerializer(user).data
#             })

#         # Si el código 2FA es incorrecto
#         return Response({"detail": "Código MFA inválido"}, status=400)

# class MFALoginVerifyView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         # Obtener datos de la solicitud
#         token = request.data.get("temp_token")
#         code = request.data.get("code")

#         # Validar datos incompletos
#         if not token or not code:
#             return Response({"detail": "Datos incompletos"}, status=400)

#         try:
#             # Verificar el token temporal
#             access_token = AccessToken(token)
#             user_id = access_token['user_id']
#             user = Usuario.objects.get(id=user_id)
#         except KeyError:
#             return Response({"detail": "Token mal formado"}, status=400)
#         except Usuario.DoesNotExist:
#             raise NotFound({"detail": "Usuario no encontrado"})

#         # Verificar si el usuario tiene habilitado 2FA
#         if not user.mfa_secret:
#             return Response({"detail": "2FA no habilitado para este usuario"}, status=400)

#         # Verificar el código de 2FA
#         totp = pyotp.TOTP(user.mfa_secret)
#         if totp.verify(code):
#             # Si el código es válido, generar nuevos tokens
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 'access': str(refresh.access_token),
#                 'refresh': str(refresh),
#                 'user': UsuarioSerializer(user).data
#             })

#         # Si el código 2FA es incorrecto
#         return Response({"detail": "Código MFA inválido"}, status=400)
            # class MFALoginVerifyView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         token = request.data.get("temp_token")
#         code = request.data.get("code")

#         if not token or not code:
#             return Response({"detail": "Datos incompletos"}, status=400)

#         try:
#             access_token = AccessToken(token)
#             user_id = access_token['user_id']
#             user = Usuario.objects.get(id=user_id)
#         except:
#             return Response({"detail": "Token inválido"}, status=400)

#         totp = pyotp.TOTP(user.mfa_secret)
#         if totp.verify(code):
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 'access': str(refresh.access_token),
#                 'refresh': str(refresh),
#                 'user': UsuarioSerializer(user).data
#             })
#         return Response({"detail": "Código MFA inválido"}, status=400)


# --- /home/runner/workspace/accounts/tests/test_auth.py ---
# accounts/tests/test_auth.py

from rest_framework.test import APITestCase
from django.urls import reverse
from accounts.models import Usuario
from rest_framework import status

class AuthTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )

    def test_login(self):
        url = reverse("login")  # Asegúrate de tener 'name="login"' en tu URL
        response = self.client.post(url, {"username": "testuser", "password": "testpass123"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_profile_access(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("profile")  # Asegúrate de tener 'name="profile"'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "testuser")

    def test_register_user(self):
        url = reverse("register")
        data = {
            "username": "newuser",
            "password": "newpass123",
            "email": "newuser@example.com"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Usuario.objects.filter(username="newuser").exists())

def test_login_fail(self):
    url = reverse("login")
    response = self.client.post(url, {"username": "wronguser", "password": "wrongpass"})
    self.assertEqual(response.status_code, 401)


# --- /home/runner/workspace/accounts/tests/test_accounts_full.py ---
# ✅ TESTS AUTOMATIZADOS COMPLETOS PARA accounts
# Archivo sugerido: accounts/tests/test_accounts_full.py

from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from accounts.models import Usuario, Rol
from rest_framework_simplejwt.tokens import RefreshToken
import pyotp

class AccountsFullTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )
        self.admin = Usuario.objects.create_superuser(
            username="admin",
            password="adminpass",
            email="admin@example.com"
        )

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_logout(self):
        self.authenticate(self.user)
        url = reverse("logout")
        refresh = str(RefreshToken.for_user(self.user))
        response = self.client.post(url, {"refresh": refresh})
        self.assertEqual(response.status_code, 205)

    def test_password_reset(self):
        url_request = reverse("password_reset_request")
        response = self.client.post(url_request, {"email": self.user.email})
        self.assertEqual(response.status_code, 200)
        # Aquí deberías simular el envío de token y confirmar el cambio

    def test_user_crud(self):
        self.authenticate(self.admin)
        url = reverse("usuarios-list")
        data = {"username": "nuevo", "password": "pass", "email": "nuevo@example.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_role_crud(self):
        self.authenticate(self.admin)
        url = reverse("roles-list")
        data = {"nombre": "Supervisor"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_2fa_enable_and_verify(self):
        self.authenticate(self.user)
        url_enable = reverse("2fa-enable")
        response = self.client.post(url_enable)
        self.assertEqual(response.status_code, 200)

        totp = pyotp.TOTP(self.user.mfa_secret)
        code = totp.now()
        url_verify = reverse("2fa-verify")
        response = self.client.post(url_verify, {"code": code})
        self.assertEqual(response.status_code, 200)


# --- /home/runner/workspace/accounts/tests/test_security.py ---
from rest_framework.test import APITestCase
from django.urls import reverse
from accounts.models import Usuario
from rest_framework_simplejwt.tokens import RefreshToken
import pyotp

class SeguridadTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username="testuser", password="Test1234", email="test@example.com"
        )

    def test_login_fail_auditoria(self):
        url = reverse("login")
        response = self.client.post(url, {"username": "wrong", "password": "bad"})
        self.assertEqual(response.status_code, 401)

    def test_login_con_mfa(self):
        self.user.mfa_enabled = True
        self.user.mfa_secret = pyotp.random_base32()
        self.user.save()

        url = reverse("login")
        response = self.client.post(url, {"username": "testuser", "password": "Test1234"})
        self.assertEqual(response.status_code, 202)
        self.assertIn("temp_token", response.data)

        # MFA TOTP correcto
        totp = pyotp.TOTP(self.user.mfa_secret)
        code = totp.now()
        verify_url = reverse("mfa-verify-login")
        response = self.client.post(verify_url, {"temp_token": response.data["temp_token"], "code": code})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

# CORS correctamente configurado:
# Solo responde a dominios permitidos:


# // En frontend en local
# fetch('https://api.tusitio.com/api/login')
# → debe fallar si el dominio no está en CORS_ALLOWED_ORIGINS
# Rate Limiting activado:
# Lanza 10 peticiones rápidas y ve si responde:


# {
#   "detail": "Request was throttled. Expected available in X seconds."
# }


# --- /home/runner/workspace/accounts/migrations/__init__.py ---



# --- /home/runner/workspace/accounts/migrations/0001_initial.py ---
# Generated by Django 5.2.4 on 2025-07-05 06:49

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Rol',
                'verbose_name_plural': 'Roles',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('mfa_enabled', models.BooleanField(default=False)),
                ('mfa_secret', models.CharField(blank=True, max_length=32, null=True)),
                ('username', models.CharField(max_length=150, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('activo', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('fecha_creacion', models.DateTimeField(default=django.utils.timezone.now)),
                ('foto', models.URLField(blank=True, null=True)),
                ('telefono', models.CharField(blank=True, max_length=30, null=True)),
                ('direccion', models.TextField(blank=True, null=True)),
                ('idioma', models.CharField(default='es', max_length=10)),
                ('tema', models.CharField(default='claro', max_length=50)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usuarios', to='core.empresa')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('rol', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='usuarios', to='accounts.rol')),
            ],
            options={
                'verbose_name': 'Usuario',
                'verbose_name_plural': 'Usuarios',
                'ordering': ['username'],
            },
        ),
        migrations.CreateModel(
            name='Auditoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accion', models.CharField(max_length=255)),
                ('tabla_afectada', models.CharField(max_length=255)),
                ('registro_afectado', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auditorias', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Auditoría',
                'verbose_name_plural': 'Auditorías',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='usuario',
            index=models.Index(fields=['empresa', 'username'], name='accounts_us_empresa_e6cf50_idx'),
        ),
        migrations.AddIndex(
            model_name='usuario',
            index=models.Index(fields=['rol', 'activo'], name='accounts_us_rol_id_e34ea6_idx'),
        ),
    ]



# --- /home/runner/workspace/accounts/migrations/0002_auditoria_username_intentado_alter_auditoria_usuario.py ---
# Generated by Django 5.2.4 on 2025-07-07 16:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditoria',
            name='username_intentado',
            field=models.CharField(blank=True, help_text='Nombre de usuario usado en caso de login fallido', max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='auditoria',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='auditorias', to=settings.AUTH_USER_MODEL),
        ),
    ]



# --- /home/runner/workspace/accounts/utils/auditoria.py ---
def registrar_auditoria(usuario=None, accion="", tabla="", registro="", username_intentado=None):
    from accounts.models import Auditoria

    if not usuario and not username_intentado:
        raise ValueError("Se debe proporcionar 'usuario' o 'username_intentado' para la auditoría.")

    Auditoria.objects.create(
        usuario=usuario if hasattr(usuario, 'id') else None,
        username_intentado=username_intentado,
        accion=accion,
        tabla_afectada=tabla,
        registro_afectado=str(registro)
    )

# def registrar_auditoria(usuario, accion, tabla, registro):
#   from accounts.models import Auditoria

#   Auditoria.objects.create(
#       usuario=usuario if hasattr(usuario, 'id') else None,
#       accion=accion,
#       tabla_afectada=tabla,
#       registro_afectado=str(registro)
#   )


