
# --- /home/runner/workspace/accounts/__init__.py ---



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



# --- /home/runner/workspace/accounts/admin.py ---
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, Permission
from accounts.models import Usuario, Rol, Auditoria

# 🔐 Usuario Admin
@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'empresa', 'rol', 'is_active', 'last_login')
    list_filter = ('rol', 'empresa', 'is_active', 'is_superuser')
    search_fields = ('username', 'email', 'rol__nombre', 'empresa__nombre')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('email', 'empresa', 'rol')}),
        ('Permisos del Sistema', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Accesos y Registro', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'empresa', 'rol', 'password1', 'password2',
                       'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )

# 🔧 Rol Admin
@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)
    ordering = ('nombre',)

# 🕵️ Auditoría Admin (Solo lectura)
@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'accion', 'tabla_afectada', 'registro_afectado', 'timestamp')
    list_filter = ('accion', 'tabla_afectada', 'timestamp')
    search_fields = ('usuario__username', 'accion', 'tabla_afectada', 'registro_afectado')
    readonly_fields = ('usuario', 'accion', 'tabla_afectada', 'registro_afectado', 'timestamp')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# ✅ Permitir gestionar permisos y grupos desde el admin
admin.site.unregister(Group)
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('permissions',)

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'content_type')
    list_filter = ('content_type',)
    search_fields = ('name', 'codename')


# # accounts/admin.py
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from accounts.models import Usuario, Rol, Auditoria

# @admin.register(Usuario)
# class UsuarioAdmin(BaseUserAdmin):
#     list_display = ('username', 'email', 'empresa', 'rol')  # elimina is_staff, is_active
#     list_filter = ('rol', 'empresa')  # elimina is_staff, is_active

#     # Campos para el formulario de edición
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Información Personal', {'fields': ('email', 'empresa', 'rol')}),
#         ('Permisos', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
#     )

#     # Campos que se usarán para crear usuario
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'email', 'empresa', 'rol', 'password1', 'password2', 'is_staff', 'is_active')}
#         ),
#     )

#     search_fields = ('username', 'email')
#     ordering = ('username',)

# @admin.register(Rol)
# class RolAdmin(admin.ModelAdmin):
#     list_display = ('nombre', 'descripcion')
#     list_display = ('nombre', 'descripcion')


# @admin.register(Auditoria)
# class AuditoriaAdmin(admin.ModelAdmin):
#     list_display = ('usuario', 'accion', 'tabla_afectada', 'timestamp')
#     list_filter = ('accion', 'tabla_afectada', 'timestamp')
#     search_fields = ('usuario__username', 'accion', 'tabla_afectada', 'registro_afectado')
#     readonly_fields = ('usuario', 'accion', 'tabla_afectada', 'registro_afectado', 'timestamp')

#     def has_add_permission(self, request):
#         return False  # No se permite agregar registros manualmente

#     def has_delete_permission(self, request, obj=None):
#         return False  # Opcional: impedir borrar registros para mantener integridad


# --- /home/runner/workspace/accounts/signals.py ---
# accounts/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from accounts.models import Auditoria, Usuario
from django.conf import settings
import threading
from django.contrib.auth.models import Group
from accounts.models import Usuario

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

@receiver(post_save, sender=Usuario)
def sync_user_group(sender, instance, **kwargs):
    if instance.rol:
        group, created = Group.objects.get_or_create(name=instance.rol.nombre)
        instance.groups.set([group])
    else:
        instance.groups.clear()


# --- /home/runner/workspace/accounts/apps.py ---
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import accounts.signals  # conecta señales


# --- /home/runner/workspace/accounts/urls.py ---
# accounts/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importación de vistas por módulos
from accounts.views import auth, profile, password_reset, mfa, audit, users
from accounts.views.roles import RoleViewSet 
from accounts.views.users import UsuarioViewSet
from accounts.views.audit import AuditLogListView, AuditLogExportCSV
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views.mfa import MFAEnableView, MFAVerifyView, MFADisableView, MFALoginVerifyView

from accounts.views.groups import GroupViewSet
from accounts.views.permissions import PermissionViewSet



# Rutas registradas con router para vistas basadas en ViewSet
router = DefaultRouter()
router.register(r'users', UsuarioViewSet, basename='usuarios')
router.register(r'roles', RoleViewSet )
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'permissions', PermissionViewSet, basename='permission')

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
    path('password-reset/confirm/', password_reset.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    # path('password-reset/confirm/', password_reset.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),  # POST - Confirmar reinicio

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


    path('', include(router.urls)),

]

# urlpatterns += router.urls



# --- /home/runner/workspace/accounts/schema.py ---
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import OpenApiResponse

class CustomAutoSchema(AutoSchema):
    def get_responses(self):
        responses = super().get_responses()

        common_errors = {
            '400': OpenApiResponse(description='Bad Request'),
            '401': OpenApiResponse(description='Unauthorized'),
            '403': OpenApiResponse(description='Forbidden'),
            '404': OpenApiResponse(description='Not Found'),
            '500': OpenApiResponse(description='Internal Server Error'),
        }

        # Solo agregar los errores que no estén ya
        for code, response in common_errors.items():
            if code not in responses:
                responses[code] = response

        return responses


# from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse
# from rest_framework import viewsets

# @extend_schema_view(
#     post=extend_schema(
#         summary="Login",
#         description="Autenticación con JWT",
#         responses={
#             200: OpenApiResponse(description="Login exitoso"),
#             400: OpenApiResponse(description="Datos inválidos"),
#             401: OpenApiResponse(description="Credenciales incorrectas"),
#             500: OpenApiResponse(description="Error interno"),
#         },
#     ),
#     get=extend_schema(
#         summary="Ver perfil",
#         description="Datos del usuario autenticado",
#         responses={
#             200: OpenApiResponse(description="Datos del usuario"),
#             401: OpenApiResponse(description="Token inválido o no enviado"),
#         },
#     ),
# )
# class AuthViewSet(viewsets.ViewSet):
#     pass



# --- /home/runner/workspace/accounts/constants.py ---
# accounts/constants.py

class Roles:
    SUPERADMIN = "Superadministrador"
    ADMIN_EMPRESA = "Administrador de Empresa"
    VENDEDOR = "Vendedor"
    INVENTARIO = "Almacén / Inventario"
    COMPRAS = "Compras / Proveedores"
    CONTADOR = "Contador"
    TESORERO = "Tesorero / Finanzas"
    RH = "Recursos Humanos"
    AUDITOR = "Auditor / Legal"
    CLIENTE = "Cliente externo"


# --- /home/runner/workspace/accounts/permissions.py ---
# accounts/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS
from accounts.constants import Roles

class IsEmpleado(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.rol and
            request.user.rol.nombre == "Empleado"
        )


class IsSuperAdminOrEmpresaAdminOrReadOnly(BasePermission):
    """
    Solo SuperAdmin puede eliminar, Admin Empresa puede crear y actualizar,
    otros roles solo lectura (GET)
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True  # lectura para todos autenticados

        if request.method == 'DELETE':
            return user.rol.nombre == Roles.SUPERADMIN

        if request.method in ['POST', 'PUT', 'PATCH']:
            return user.rol.nombre in [Roles.SUPERADMIN, Roles.ADMIN_EMPRESA]

        return False


# 🔐 Permisos base por rol exacto (uno por clase)
class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.SUPERADMIN

class IsEmpresaAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.ADMIN_EMPRESA

class IsVendedor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.VENDEDOR

class IsInventario(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.INVENTARIO

class IsCompras(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.COMPRAS

class IsContador(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.CONTADOR

class IsTesorero(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.TESORERO

class IsRecursosHumanos(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.RH

class IsAuditor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.AUDITOR

class IsClienteExterno(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.CLIENTE


# 🔁 Combinaciones comunes (útiles para reutilizar en muchas vistas)

class IsSuperAdminOrEmpresaAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.SUPERADMIN, Roles.ADMIN_EMPRESA
        ]

class IsSuperAdminOrVendedor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.SUPERADMIN, Roles.VENDEDOR
        ]

class IsSuperAdminOrInventario(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.SUPERADMIN, Roles.INVENTARIO
        ]

class IsSuperAdminOrCompras(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.SUPERADMIN, Roles.COMPRAS
        ]

class IsSuperAdminOrContador(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.SUPERADMIN, Roles.CONTADOR
        ]

class IsSuperAdminOrTesorero(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.SUPERADMIN, Roles.TESORERO
        ]

class IsSuperAdminOrRecursosHumanos(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.SUPERADMIN, Roles.RH
        ]

class IsSuperAdminOrAuditor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.SUPERADMIN, Roles.AUDITOR
        ]

class IsEmpresaAdminOrVendedor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.ADMIN_EMPRESA, Roles.VENDEDOR
        ]


# 🔀 Helper dinámico para múltiples combinaciones OR
def OrPermissions(*perms):
    class _OrPermission(BasePermission):
        def has_permission(self, request, view):
            return any(perm().has_permission(request, view) for perm in perms)
    return _OrPermission


# 🛡️ Permisos basados en codename de Django (add_modelo, view_modelo, etc.)
def CustomPermission(permiso_codename):
    class _CustomPermission(BasePermission):
        def has_permission(self, request, view):
            return request.user.is_authenticated and request.user.has_perm(permiso_codename)
    return _CustomPermission




class IsAdminOrReadOnly(BasePermission):
    """
    Permite solo lectura a usuarios normales.
    Permite lectura y escritura a SuperAdmin o AdminEmpresa.
    """
    def has_permission(self, request, view):
        # Si el método es seguro (GET, HEAD, OPTIONS), se permite a todos los autenticados
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Si es escritura (POST, PUT, DELETE...), solo Admins
        return (
            request.user.is_authenticated and
            request.user.rol.nombre in ["Superadministrador", "Administrador"]
        )


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

from django.contrib.auth.models import Group

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
    grupo = models.OneToOneField(Group, on_delete=models.SET_NULL, null=True, blank=True)

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
    sucursal_actual = models.ForeignKey(
        'core.Sucursal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios_actuales'
    )

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

    # def __str__(self):
    #     return self.username

    def __str__(self):
        empresa_nombre = self.empresa.nombre if self.empresa else "Sin empresa"
        return f"{self.username} ({self.email}) - {empresa_nombre}"

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username




# --- /home/runner/workspace/accounts/views/__init__.py ---
from .auth import *
from .profile import *
from .password_reset import *
from .mfa import *
from .audit import *
from .users import *
from .roles import *


# --- /home/runner/workspace/accounts/views/groups.py ---
# 🧩 Django
from django.contrib.auth.models import Group

# 🛠️ Django REST Framework
from rest_framework import viewsets

# 📦 Serializers
from accounts.serializers.group_permission_serializers import GroupSerializer

# 🔐 Permisos personalizados
from accounts.permissions import IsSuperAdmin, CustomPermission


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Solo SuperAdmin puede modificar grupos
            return [IsSuperAdmin()]
        elif self.action in ['list', 'retrieve']:
            # Ver grupos requiere permiso explícito de Django
            return [CustomPermission('auth.view_group')()]
        # Fallback seguro
        return [IsSuperAdmin()]

# from django.contrib.auth.models import Group
# from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated

# from accounts.serializers.group_permission_serializers import GroupSerializer

# class GroupViewSet(viewsets.ModelViewSet):
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer
#     permission_classes = [IsAuthenticated]  # O usa tu CustomPermission



# --- /home/runner/workspace/accounts/views/mfa.py ---
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from datetime import timedelta
import pyotp

from accounts.models import Usuario
from accounts.serializers.mfa_serializers import (
    MFAEnableSerializer,
    MFAVerifySerializer,
    MFADisableSerializer
)
from accounts.serializers.user_serializers import UsuarioSerializer
from accounts.utils.auditoria import registrar_auditoria

# 🔐 Roles permitidos (definidos previamente en accounts.constants.Roles)
from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsEmpleado, IsAuditor


def generate_temp_token(user):
    access_token = AccessToken.for_user(user)
    access_token.set_exp(lifetime=timedelta(minutes=5))  # Token válido solo 5 minutos
    return str(access_token)


class MFAEnableView(APIView):
    permission_classes = [IsAuthenticated]  # Se puede reforzar con IsEmpresaAdmin | IsEmpleado
    serializer_class = MFAEnableSerializer

    def post(self, request):
        user = request.user
        if user.mfa_enabled:
            return Response({"detail": "MFA ya está activado."}, status=status.HTTP_400_BAD_REQUEST)

        secret = pyotp.random_base32()
        user.mfa_secret = secret
        user.save()

        otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.username,
            issuer_name="Nova ERP"
        )

        return Response({"otp_uri": otp_uri, "secret": secret})


class MFAVerifyView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MFAVerifySerializer

    def post(self, request):
        user = request.user
        serializer = MFAVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']

        if not user.mfa_secret:
            return Response({"detail": "MFA no está configurado para este usuario."}, status=400)

        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(code):
            user.mfa_enabled = True
            user.save()
            registrar_auditoria(user, "MFA_ACTIVADO", "Usuario", "MFA activado correctamente")
            return Response({"detail": "MFA activado correctamente."})

        registrar_auditoria(user, "MFA_FALLIDO", "Usuario", "Código MFA inválido")
        return Response({"detail": "Código MFA inválido. Intenta de nuevo."}, status=400)


class MFADisableView(APIView):
    permission_classes = [IsAuthenticated]  # Se puede reforzar con IsEmpresaAdmin | IsEmpleado
    serializer_class = MFADisableSerializer

    def post(self, request):
        user = request.user
        serializer = MFADisableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']

        if not user.mfa_enabled:
            return Response({"detail": "MFA no está activado."}, status=400)

        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(code):
            user.mfa_enabled = False
            user.mfa_secret = ""
            user.save()
            registrar_auditoria(user, "MFA_DESACTIVADO", "Usuario", "MFA desactivado")
            return Response({"detail": "MFA desactivado correctamente."})

        return Response({"detail": "Código inválido."}, status=400)


class MFALoginVerifyView(APIView):
    permission_classes = [AllowAny]
    serializer_class = MFAVerifySerializer

    def post(self, request):
        token = request.data.get("temp_token")
        code = request.data.get("code")

        if not token or not code:
            return Response({"detail": "Datos incompletos"}, status=400)

        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = Usuario.objects.get(id=user_id)
        except TokenError as e:
            return Response({"detail": "Token inválido o expirado", "error": str(e)}, status=401)
        except KeyError:
            return Response({"detail": "Token mal formado"}, status=400)
        except Usuario.DoesNotExist:
            return Response({"detail": "Usuario no encontrado"}, status=404)

        if not user.mfa_secret:
            return Response({"detail": "2FA no habilitado para este usuario"}, status=400)

        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(code):
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UsuarioSerializer(user).data
            })

        return Response({"detail": "Código MFA inválido"}, status=400)

# # from rest_framework.permissions import AllowAny
# # # Standard Library
# # from datetime import timedelta
# # import pyotp

# # # Django REST Framework
# # from rest_framework.views import APIView
# # from rest_framework.response import Response
# # from rest_framework.permissions import IsAuthenticated
# # from rest_framework import status
# # from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
# # from rest_framework_simplejwt.exceptions import TokenError

# # # App local
# # from accounts.models import Usuario
# # from accounts.serializers.mfa_serializers import (
# #     MFAEnableSerializer,
# #     MFAVerifySerializer,
# #     MFADisableSerializer
# # )
# # from accounts.serializers.user_serializers import UsuarioSerializer
# # from accounts.utils.auditoria import registrar_auditoria

# # from rest_framework import serializers



# # def generate_temp_token(user):
# #     # Crear un AccessToken para el usuario
# #     access_token = AccessToken.for_user(user)
# #     # Aquí puedes agregar más datos si es necesario
# #     access_token.set_exp(lifetime=timedelta(minutes=5))  # Establecer un tiempo de expiración corto
# #     return str(access_token)

# # class MFAEnableView(APIView):
# #     permission_classes = [IsAuthenticated]
# #     serializer_class = MFAEnableSerializer

# #     def post(self, request):
# #         user = request.user
# #         if user.mfa_enabled:
# #             return Response({"detail": "MFA ya está activado."}, status=status.HTTP_400_BAD_REQUEST)

# #         # Generar nuevo secreto
# #         secret = pyotp.random_base32()
# #         user.mfa_secret = secret
# #         user.save()

# #         # Generar URL para QR (otpauth)
# #         otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
# #             name=user.username, issuer_name="Nova ERP"
# #         )

# #         return Response({
# #             "otp_uri": otp_uri,
# #             "secret": secret,  # opcional mostrar clave manualmente
# #         })

# # class MFAVerifyView(APIView):
# #     permission_classes = [IsAuthenticated]
# #     serializer_class = MFAVerifySerializer
    
# #     def post(self, request):
# #         user = request.user
# #         serializer = MFAVerifySerializer(data=request.data)

# #         # Verificar que los datos del serializer son válidos
# #         serializer.is_valid(raise_exception=True)

# #         # Obtener el código MFA del serializer
# #         code = serializer.validated_data['code']

# #         # Verificar si el usuario tiene configurado MFA
# #         if not user.mfa_secret:
# #             return Response(
# #                 {"detail": "MFA no está configurado para este usuario."}, 
# #                 status=status.HTTP_400_BAD_REQUEST
# #             )

# #         # Generar el objeto TOTP y verificar el código
# #         totp = pyotp.TOTP(user.mfa_secret)
# #         if totp.verify(code):
# #             # Si el código es válido, habilitar MFA para el usuario
# #             user.mfa_enabled = True
# #             user.save()

# #             # Registrar la auditoría para activación exitosa
# #             registrar_auditoria(user, "MFA_ACTIVADO", "Usuario", "MFA activado correctamente")

# #             return Response({"detail": "MFA activado correctamente."})
# #         else:
# #             # Registrar la auditoría para intento fallido
# #             registrar_auditoria(user, "MFA_FALLIDO", "Usuario", "Código MFA inválido")

# #             return Response(
# #                 {"detail": "Código MFA inválido. Por favor, intente nuevamente."}, 
# #                 status=status.HTTP_400_BAD_REQUEST
# #             )



# # class MFADisableView(APIView):
# #     permission_classes = [IsAuthenticated]
# #     serializer_class = MFADisableSerializer

# #     def post(self, request):
# #         user = request.user
# #         serializer = MFADisableSerializer(data=request.data)
# #         serializer.is_valid(raise_exception=True)

# #         code = serializer.validated_data['code']
# #         if not user.mfa_enabled:
# #             return Response({"detail": "MFA no está activado."}, status=status.HTTP_400_BAD_REQUEST)

# #         totp = pyotp.TOTP(user.mfa_secret)
# #         if totp.verify(code):
# #             user.mfa_enabled = False
# #             user.mfa_secret = ""
# #             user.save()
# #             registrar_auditoria(user, "MFA_DESACTIVADO", "Usuario", "MFA desactivado")
# #             return Response({"detail": "MFA desactivado correctamente."})
# #         else:
# #             return Response({"detail": "Código inválido."}, status=status.HTTP_400_BAD_REQUEST)




# # class MFALoginVerifyView(APIView):
# #     permission_classes = [AllowAny]
# #     serializer_class = MFAVerifySerializer

# #     def post(self, request):
# #         token = request.data.get("temp_token")
# #         code = request.data.get("code")

# #         if not token or not code:
# #             return Response({"detail": "Datos incompletos"}, status=400)

# #         try:
# #             access_token = AccessToken(token)
# #             user_id = access_token['user_id']
# #             user = Usuario.objects.get(id=user_id)
# #         except TokenError as e:
# #             return Response({"detail": "Token inválido o expirado", "error": str(e)}, status=401)
# #         except KeyError:
# #             return Response({"detail": "Token mal formado"}, status=400)
# #         except Usuario.DoesNotExist:
# #             return Response({"detail": "Usuario no encontrado"}, status=404)

# #         if not user.mfa_secret:
# #             return Response({"detail": "2FA no habilitado para este usuario"}, status=400)

# #         totp = pyotp.TOTP(user.mfa_secret)
# #         if totp.verify(code):
# #             refresh = RefreshToken.for_user(user)
# #             return Response({
# #                 'access': str(refresh.access_token),
# #                 'refresh': str(refresh),
# #                 'user': UsuarioSerializer(user).data
# #             })

# #         return Response({"detail": "Código MFA inválido"}, status=400)


# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
# from rest_framework_simplejwt.exceptions import TokenError
# from datetime import timedelta
# import pyotp

# from accounts.models import Usuario
# from accounts.serializers.mfa_serializers import MFAEnableSerializer, MFAVerifySerializer, MFADisableSerializer
# from accounts.serializers.user_serializers import UsuarioSerializer
# from accounts.utils.auditoria import registrar_auditoria


# def generate_temp_token(user):
#     access_token = AccessToken.for_user(user)
#     access_token.set_exp(lifetime=timedelta(minutes=5))  # Token válido solo 5 minutos
#     return str(access_token)


# class MFAEnableView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = MFAEnableSerializer

#     def post(self, request):
#         user = request.user
#         if user.mfa_enabled:
#             return Response({"detail": "MFA ya está activado."}, status=status.HTTP_400_BAD_REQUEST)

#         secret = pyotp.random_base32()
#         user.mfa_secret = secret
#         user.save()

#         otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user.username, issuer_name="Nova ERP")

#         return Response({"otp_uri": otp_uri, "secret": secret})


# class MFAVerifyView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = MFAVerifySerializer

#     def post(self, request):
#         user = request.user
#         serializer = MFAVerifySerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         code = serializer.validated_data['code']

#         if not user.mfa_secret:
#             return Response({"detail": "MFA no está configurado para este usuario."}, status=status.HTTP_400_BAD_REQUEST)

#         totp = pyotp.TOTP(user.mfa_secret)
#         if totp.verify(code):
#             user.mfa_enabled = True
#             user.save()
#             registrar_auditoria(user, "MFA_ACTIVADO", "Usuario", "MFA activado correctamente")
#             return Response({"detail": "MFA activado correctamente."})
#         else:
#             registrar_auditoria(user, "MFA_FALLIDO", "Usuario", "Código MFA inválido")
#             return Response({"detail": "Código MFA inválido. Intenta de nuevo."}, status=status.HTTP_400_BAD_REQUEST)


# class MFADisableView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = MFADisableSerializer

#     def post(self, request):
#         user = request.user
#         serializer = MFADisableSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         code = serializer.validated_data['code']

#         if not user.mfa_enabled:
#             return Response({"detail": "MFA no está activado."}, status=status.HTTP_400_BAD_REQUEST)

#         totp = pyotp.TOTP(user.mfa_secret)
#         if totp.verify(code):
#             user.mfa_enabled = False
#             user.mfa_secret = ""
#             user.save()
#             registrar_auditoria(user, "MFA_DESACTIVADO", "Usuario", "MFA desactivado")
#             return Response({"detail": "MFA desactivado correctamente."})
#         else:
#             return Response({"detail": "Código inválido."}, status=status.HTTP_400_BAD_REQUEST)


# class MFALoginVerifyView(APIView):
#     permission_classes = [AllowAny]
#     serializer_class = MFAVerifySerializer

#     def post(self, request):
#         token = request.data.get("temp_token")
#         code = request.data.get("code")

#         if not token or not code:
#             return Response({"detail": "Datos incompletos"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             access_token = AccessToken(token)
#             user_id = access_token['user_id']
#             user = Usuario.objects.get(id=user_id)
#         except TokenError as e:
#             return Response({"detail": "Token inválido o expirado", "error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
#         except KeyError:
#             return Response({"detail": "Token mal formado"}, status=status.HTTP_400_BAD_REQUEST)
#         except Usuario.DoesNotExist:
#             return Response({"detail": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

#         if not user.mfa_secret:
#             return Response({"detail": "2FA no habilitado para este usuario"}, status=status.HTTP_400_BAD_REQUEST)

#         totp = pyotp.TOTP(user.mfa_secret)
#         if totp.verify(code):
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 'access': str(refresh.access_token),
#                 'refresh': str(refresh),
#                 'user': UsuarioSerializer(user).data
#             })

#         return Response({"detail": "Código MFA inválido"}, status=status.HTTP_400_BAD_REQUEST)



# --- /home/runner/workspace/accounts/views/password_reset.py ---
# Django
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

# Django REST Framework
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

# Utilidades
import pyotp

# App local
from accounts.models import Usuario
from accounts.utils.auditoria import registrar_auditoria
from accounts.serializers.auth_serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

# Configuración del sitio (ajusta si usas variable de entorno)
site_url = "fca3faea-e64a-4f83-a448-762fa6e71df4-00-1kkfg9j97gplb.spock.replit.dev"
# Ej: site_url = os.environ.get("SITE_URL")


# 📤 Enviar correo de recuperación
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = Usuario.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            reset_url = f"https://{site_url}/api/auth/password-reset/confirm/?uidb64={uidb64}&token={token}"

            send_mail(
                subject="Recuperación de contraseña - Nova ERP",
                message=f"Haz clic en el siguiente enlace para restablecer tu contraseña:\n\n{reset_url}",
                from_email="no-reply@novaerp.com",
                recipient_list=[email],
                fail_silently=False,
            )

            registrar_auditoria(user, "RESET_SOLICITADO", "Usuario", "Solicitud de recuperación de contraseña")
            return Response({"msg": "Correo enviado para recuperación de contraseña"}, status=status.HTTP_200_OK)

        except Usuario.DoesNotExist:
            # Por seguridad, se devuelve siempre éxito
            return Response({"msg": "Correo enviado para recuperación de contraseña"}, status=status.HTTP_200_OK)


# ✅ Confirmar cambio de contraseña
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = serializer.validated_data['uidb64']
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        code = serializer.validated_data.get('code')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            return Response({"error": "Usuario inválido"}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Token inválido o expirado"}, status=status.HTTP_400_BAD_REQUEST)

        # Si tiene MFA habilitado
        if getattr(user, 'mfa_enabled', False):
            if not code:
                return Response({"error": "Código MFA requerido"}, status=status.HTTP_400_BAD_REQUEST)

            totp = pyotp.TOTP(user.mfa_secret)
            if not totp.verify(code):
                registrar_auditoria(user, "RESET_MFA_FAIL", "Usuario", "Código MFA inválido en recuperación")
                return Response({"error": "Código MFA inválido"}, status=status.HTTP_400_BAD_REQUEST)

        # Restablecer contraseña
        user.set_password(password)
        user.save()
        registrar_auditoria(user, "RESET_PASSWORD", "Usuario", "Contraseña restablecida exitosamente")
        return Response({"msg": "Contraseña cambiada correctamente"}, status=status.HTTP_200_OK)

# # Django
# from django.core.mail import send_mail
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_str

# # Django REST Framework
# from rest_framework import status, serializers
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny

# # App local
# from accounts.models import Usuario
# from accounts.utils.auditoria import registrar_auditoria
# from accounts.serializers.auth_serializers import (
#     PasswordResetRequestSerializer,
#     PasswordResetConfirmSerializer
# )

# import pyotp


# site_url = "fca3faea-e64a-4f83-a448-762fa6e71df4-00-1kkfg9j97gplb.spock.replit.dev"


# # ----------------------------------------
# # 🔐 SERIALIZERS (si ya los tienes en accounts.serializers.auth_serializers, no repitas aquí)
# # ----------------------------------------
# # class PasswordResetRequestSerializer(serializers.Serializer):
# #     email = serializers.EmailField()

# # class PasswordResetConfirmSerializer(serializers.Serializer):
# #     uidb64 = serializers.CharField()
# #     token = serializers.CharField()
# #     password = serializers.CharField(min_length=8)
# #     code = serializers.CharField(required=False)  # Solo si tiene MFA


# # ----------------------------------------
# # 📤 SOLICITUD DE RECUPERACIÓN
# # ----------------------------------------

# class PasswordResetRequestView(APIView):
#     permission_classes = [AllowAny]
#     serializer_class = PasswordResetRequestSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         email = serializer.validated_data['email']

#         try:
#             user = Usuario.objects.get(email=email)
#             token = default_token_generator.make_token(user)
#             uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

#             reset_url = f"https://{site_url}/api/auth/password-reset/confirm/?uidb64={uidb64}&token={token}"
#             send_mail(
#                 subject="Recupera tu contraseña",
#                 message=f"Enlace para resetear: {reset_url}",
#                 from_email="no-reply@erp.com",
#                 recipient_list=[email],
#                 fail_silently=False,
#             )
#             return Response({"msg": "Email enviado"}, status=status.HTTP_200_OK)

#         except Usuario.DoesNotExist:
#             # Para no revelar si el email existe o no, puedes devolver éxito aquí también (mejor seguridad)
#             return Response({"msg": "Email enviado"}, status=status.HTTP_200_OK)
#             # Si quieres indicar que no existe:
#             # return Response({"error": "Email no registrado"}, status=status.HTTP_404_NOT_FOUND)


# # ----------------------------------------
# # ✅ CONFIRMACIÓN DEL CAMBIO DE CONTRASEÑA
# # ----------------------------------------

# class PasswordResetConfirmView(APIView):
#     permission_classes = [AllowAny]
#     serializer_class = PasswordResetConfirmSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         uidb64 = serializer.validated_data['uidb64']
#         token = serializer.validated_data['token']
#         password = serializer.validated_data['password']
#         code = serializer.validated_data.get('code')

#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = Usuario.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
#             return Response({"error": "Usuario inválido"}, status=status.HTTP_400_BAD_REQUEST)

#         if default_token_generator.check_token(user, token):
#             if getattr(user, 'mfa_enabled', False):
#                 if not code:
#                     return Response({"error": "Código MFA requerido"}, status=status.HTTP_400_BAD_REQUEST)
#                 totp = pyotp.TOTP(user.mfa_secret)
#                 if not totp.verify(code):
#                     registrar_auditoria(user, "RESET_MFA_FAIL", "Usuario", "Código MFA inválido")
#                     return Response({"error": "Código MFA inválido"}, status=status.HTTP_400_BAD_REQUEST)

#             user.set_password(password)
#             user.save()
#             registrar_auditoria(user, "RESET_PASSWORD", "Usuario", "Contraseña restablecida con éxito")
#             return Response({"msg": "Contraseña cambiada correctamente"}, status=status.HTTP_200_OK)

#         return Response({"error": "Token inválido o expirado"}, status=status.HTTP_400_BAD_REQUEST)


# # # Django
# # from django.core.mail import send_mail
# # from django.contrib.auth.tokens import default_token_generator
# # from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# # from django.utils.encoding import force_bytes, force_str

# # # Django REST Framework
# # from rest_framework import status
# # from rest_framework.views import APIView
# # from rest_framework.response import Response

# # # App local
# # from accounts.models import Usuario
# # from accounts.utils.auditoria import registrar_auditoria
# # from accounts.serializers.auth_serializers import (
# #     PasswordResetRequestSerializer,
# #     PasswordResetConfirmSerializer
# # )

# # import pyotp

# # from rest_framework import serializers


# # site_url = "fca3faea-e64a-4f83-a448-762fa6e71df4-00-1kkfg9j97gplb.spock.replit.dev"

# # # ----------------------------------------
# # # 🔐 SERIALIZERS
# # # ----------------------------------------

# # class PasswordResetRequestSerializer(serializers.Serializer):
# #     email = serializers.EmailField()

# # class PasswordResetConfirmSerializer(serializers.Serializer):
# #     uidb64 = serializers.CharField()
# #     token = serializers.CharField()
# #     password = serializers.CharField(min_length=8)
# #     code = serializers.CharField(required=False)  # Solo si tiene MFA


# # # ----------------------------------------
# # # 📤 SOLICITUD DE RECUPERACIÓN
# # # ----------------------------------------

# # class PasswordResetRequestView(APIView):
# #     serializer_class = PasswordResetRequestSerializer

# #     def post(self, request):
# #         serializer = self.serializer_class(data=request.data)
# #         serializer.is_valid(raise_exception=True)
# #         email = serializer.validated_data['email']

# #         try:
# #             user = Usuario.objects.get(email=email)
# #             token = default_token_generator.make_token(user)
# #             uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

# #             reset_url = f"https://{site_url}/api/auth/password-reset/confirm/?uidb64={uidb64}&token={token}"
# #             send_mail(
# #                 subject="Recupera tu contraseña",
# #                 message=f"Enlace para resetear: {reset_url}",
# #                 from_email="no-reply@erp.com",
# #                 recipient_list=[email],
# #                 fail_silently=False,
# #             )
# #             return Response({"msg": "Email enviado"}, status=200)

# #         except Usuario.DoesNotExist:
# #             return Response({"error": "Email no registrado"}, status=404)

# # # ----------------------------------------
# # # ✅ CONFIRMACIÓN DEL CAMBIO DE CONTRASEÑA
# # # ----------------------------------------

# # class PasswordResetConfirmView(APIView):
# #     serializer_class = PasswordResetConfirmSerializer

# #     def post(self, request):
# #         serializer = self.serializer_class(data=request.data)
# #         serializer.is_valid(raise_exception=True)

# #         uidb64 = serializer.validated_data['uidb64']
# #         token = serializer.validated_data['token']
# #         password = serializer.validated_data['password']
# #         code = serializer.validated_data.get('code')

# #         try:
# #             uid = force_str(urlsafe_base64_decode(uidb64))
# #             user = Usuario.objects.get(pk=uid)
# #         except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
# #             return Response({"error": "Usuario inválido"}, status=400)

# #         if default_token_generator.check_token(user, token):
# #             if getattr(user, 'mfa_enabled', False):
# #                 if not code:
# #                     return Response({"error": "Código MFA requerido"}, status=400)
# #                 totp = pyotp.TOTP(user.mfa_secret)
# #                 if not totp.verify(code):
# #                     registrar_auditoria(user, "RESET_MFA_FAIL", "Usuario", "Código MFA inválido")
# #                     return Response({"error": "Código MFA inválido"}, status=400)

# #             user.set_password(password)
# #             user.save()
# #             registrar_auditoria(user, "RESET_PASSWORD", "Usuario", "Contraseña restablecida con éxito")
# #             return Response({"msg": "Contraseña cambiada correctamente"})

# #         return Response({"error": "Token inválido o expirado"}, status=400)



# # # ----------------------------------------
# # # ✅ CONFIRMACIÓN DEL CAMBIO DE CONTRASEÑA
# # # ----------------------------------------

# # class PasswordResetConfirmView(APIView):
# #     serializer_class = PasswordResetConfirmSerializer
# #     def post(self, request):
# #         serializer = PasswordResetConfirmSerializer(data=request.data)
# #         serializer.is_valid(raise_exception=True)

# #         uidb64 = serializer.validated_data['uidb64']
# #         token = serializer.validated_data['token']
# #         password = serializer.validated_data['password']
# #         code = serializer.validated_data.get('code')

# #         try:
# #             uid = force_str(urlsafe_base64_decode(uidb64))
# #             user = Usuario.objects.get(pk=uid)
# #         except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
# #             return Response({"error": "Usuario inválido"}, status=400)

# #         if default_token_generator.check_token(user, token):
# #             if user.mfa_enabled:
# #                 if not code:
# #                     return Response({"error": "Código MFA requerido"}, status=400)
# #                 totp = pyotp.TOTP(user.mfa_secret)
# #                 if not totp.verify(code):
# #                     registrar_auditoria(user, "RESET_MFA_FAIL", "Usuario", "Código MFA inválido")
# #                     return Response({"error": "Código MFA inválido"}, status=400)

# #             user.set_password(password)
# #             user.save()
# #             registrar_auditoria(user, "RESET_PASSWORD", "Usuario", "Contraseña restablecida con éxito")
# #             return Response({"msg": "Contraseña cambiada correctamente"})

# #         # 🔴 El token es inválido
# #         return Response({"error": "Token inválido o expirado"}, status=400)





# --- /home/runner/workspace/accounts/views/audit.py ---
# 📦 Standard library
import csv

# 🧩 Django
from django.http import HttpResponse

# 🛠️ Django REST Framework
from rest_framework import generics, filters, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

# 🔍 Filtros de terceros
from django_filters.rest_framework import DjangoFilterBackend

# 🧠 Local apps
from accounts.models import Auditoria
from accounts.serializers.auditoria_serializers import AuditoriaSerializer
from accounts.filters import AuditoriaFilter
from accounts.permissions import IsSuperAdminOrAuditor


# 🔹 Serializer vacío para cumplir con DRF en vistas sin body
class EmptySerializer(serializers.Serializer):
    pass


# ✅ Exportar auditoría a CSV (solo SuperAdmin o Auditor)
class AuditLogExportCSV(APIView):
    permission_classes = [IsSuperAdminOrAuditor]
    serializer_class = EmptySerializer

    def get(self, request):
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


# ✅ Ver historial personal del usuario autenticado
class ActivityLogView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AuditoriaSerializer

    def get(self, request):
        logs = Auditoria.objects.filter(usuario_id=request.user.id).order_by('-timestamp')[:50]
        data = self.serializer_class(logs, many=True).data
        return Response(data)


# ✅ Ver últimas 200 auditorías (solo SuperAdmin o Auditor)
class AuditLogView(APIView):
    permission_classes = [IsSuperAdminOrAuditor]
    serializer_class = AuditoriaSerializer

    def get(self, request):
        logs = Auditoria.objects.all().order_by('-timestamp')[:200]
        data = self.serializer_class(logs, many=True).data
        return Response(data)


# ✅ Paginación estándar para auditorías
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


# ✅ Lista paginada, filtrable y ordenable de auditorías
class AuditLogListView(generics.ListAPIView):
    queryset = Auditoria.objects.all()
    serializer_class = AuditoriaSerializer
    permission_classes = [IsSuperAdminOrAuditor]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AuditoriaFilter
    ordering_fields = ['timestamp', 'usuario__username', 'accion', 'tabla_afectada']
    ordering = ['-timestamp']
    pagination_class = StandardResultsSetPagination





# --- /home/runner/workspace/accounts/views/profile.py ---
from rest_framework import generics
from rest_framework.permissions import BasePermission
from accounts.serializers.user_serializers import UsuarioSerializer

# Importa tus permisos personalizados si los quieres usar aparte (aquí no son usados directamente)
from accounts.permissions import (
    IsSuperAdmin,
    IsEmpresaAdmin,
    IsVendedor,
    IsInventario,
    IsCompras,
    IsContador,
    IsTesorero,
    IsRecursosHumanos,
    IsAuditor,
    IsClienteExterno,
)

# ✅ Permiso combinado para usuarios con cualquier rol válido en el sistema
class HasValidRole(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.rol and
            request.user.rol.nombre in [
                "Superadministrador",
                "Administrador de Empresa",
                "Vendedor",
                "Almacén / Inventario",
                "Compras / Proveedores",
                "Contador",
                "Tesorero / Finanzas",
                "Recursos Humanos",
                "Auditor / Legal",
                "Cliente externo"
            ]
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [HasValidRole]

    def get_object(self):
        return self.request.user



# --- /home/runner/workspace/accounts/views/users.py ---
from rest_framework import viewsets, filters
from accounts.models import Usuario
from accounts.serializers.user_serializers import UsuarioCreateSerializer, UsuarioDetailSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied

from accounts.permissions import IsSuperAdminOrEmpresaAdmin  # permiso combinado importado

class UsuarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperAdminOrEmpresaAdmin]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['username', 'email']
    filterset_fields = ['activo', 'empresa', 'rol']

    def get_queryset(self):
        user = self.request.user

        if user.rol.nombre == "Superadministrador":
            return Usuario.objects.select_related('empresa', 'rol').all()
        elif user.rol.nombre == "Administrador de Empresa":
            return Usuario.objects.select_related('empresa', 'rol').filter(empresa=user.empresa)
        else:
            raise PermissionDenied("No tienes permisos para ver usuarios")

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioDetailSerializer

    def perform_create(self, serializer):
        user = self.request.user

        if user.rol.nombre == "Superadministrador":
            serializer.save()
        elif user.rol.nombre == "Administrador de Empresa":
            serializer.save(empresa=user.empresa)
        else:
            raise PermissionDenied("No puedes crear usuarios")

    def perform_destroy(self, instance):
        # Baja lógica: no se borra, solo se inactiva
        instance.activo = False
        instance.save()






# --- /home/runner/workspace/accounts/views/auth.py ---
# 🛡️ Django REST Framework
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.authentication import BaseAuthentication, BasicAuthentication

# 🔑 JWT
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError

# 🧾 Serializers
from accounts.serializers.auth_serializers import LoginSerializer
from accounts.serializers.user_serializers import UsuarioRegistroSerializer, UsuarioSerializer

# 🧠 Auditoría
from accounts.utils.auditoria import registrar_auditoria


# 🔹 Serializer vacío para endpoints sin entrada
class EmptySerializer(serializers.Serializer):
    pass


# 🔹 Desactiva autenticación para ciertos endpoints como login
class NoAuthentication(BaseAuthentication):
    def authenticate(self, request):
        return None


# ✅ LOGIN CON AUDITORÍA Y SOPORTE PARA MFA
class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = [NoAuthentication]  # ignora token JWT aquí

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

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


# ✅ LOGOUT CON BLACKLIST Y AUDITORÍA
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {"detail": "Se requiere el refresh token para cerrar sesión."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            registrar_auditoria(
                usuario=request.user,
                accion="LOGOUT",
                tabla="Usuario",
                registro="Logout exitoso"
            )

            return Response(
                {"detail": "Sesión cerrada correctamente."},
                status=status.HTTP_205_RESET_CONTENT
            )

        except TokenError:
            return Response(
                {"detail": "El token ya fue usado o es inválido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            return Response(
                {"detail": "Error inesperado al cerrar sesión."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ✅ REGISTRO DE USUARIOS (público o controlable por rol)
class RegisterView(generics.CreateAPIView):
    serializer_class = UsuarioRegistroSerializer
    permission_classes = [AllowAny]
    authentication_classes = [BasicAuthentication]  # útil para apps móviles o sistemas externos


# ✅ REFRESCAR TOKEN JWT
class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]




# --- /home/runner/workspace/accounts/views/permissions.py ---
from django.contrib.auth.models import Permission
from rest_framework import viewsets
from rest_framework.permissions import BasePermission

from accounts.serializers.group_permission_serializers import PermissionSerializer


# 🔐 Permiso personalizado: Solo Superadmin o Auditor/Legal
class IsSuperAdminOrAuditor(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and 
            user.rol is not None and 
            user.rol.nombre in ["Superadministrador", "Auditor / Legal"]
        )


# 📋 Vista de solo lectura para listar permisos disponibles en el sistema
class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsSuperAdminOrAuditor]





# --- /home/runner/workspace/accounts/views/roles.py ---
from rest_framework import viewsets
from accounts.models import Rol
from accounts.serializers.rol_serializers import RoleSerializer
from accounts.permissions import IsSuperAdmin , IsSuperAdminOrEmpresaAdmin # Importa tu permiso personalizado

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsSuperAdminOrEmpresaAdmin]




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



# --- /home/runner/workspace/accounts/migrations/0003_rol_grupo.py ---
# Generated by Django 5.2.4 on 2025-07-12 04:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auditoria_username_intentado_alter_auditoria_usuario'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='rol',
            name='grupo',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.group'),
        ),
    ]



# --- /home/runner/workspace/accounts/migrations/0004_usuario_sucursal_actual.py ---
# Generated by Django 5.2.4 on 2025-07-17 16:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_rol_grupo'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='sucursal_actual',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='usuarios_actuales', to='core.sucursal'),
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



# --- /home/runner/workspace/accounts/utils/assign_group_by_rol.py ---
from django.contrib.auth.models import Group

def assign_group_by_rol(user):
    if user.rol:
        group, _ = Group.objects.get_or_create(name=user.rol.nombre)
        user.groups.set([group])



# --- /home/runner/workspace/accounts/utils/__init__.py ---



# --- /home/runner/workspace/accounts/serializers/auth_serializers.py ---
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



# --- /home/runner/workspace/accounts/serializers/mfa_serializers.py ---
from rest_framework import serializers

class EnableMFASerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=["totp", "sms"])


class VerifyMFASerializer(serializers.Serializer):
    code = serializers.CharField()


class MFAEnableSerializer(serializers.Serializer):
    pass


class MFAVerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)


class MFADisableSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)



# --- /home/runner/workspace/accounts/serializers/auditoria_serializers.py ---
from rest_framework import serializers
from ..models import Auditoria

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



# --- /home/runner/workspace/accounts/serializers/__init__.py ---
from .auth_serializers import *
from .user_serializers import *
from .mfa_serializers import *
from .auditoria_serializers import *
from .rol_serializers import *


# --- /home/runner/workspace/accounts/serializers/rol_serializers.py ---
from rest_framework import serializers
from accounts.models import Rol  # Importa el modelo correctamente

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'



# --- /home/runner/workspace/accounts/serializers/group_permission_serializers.py ---
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all()
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']



# from django.contrib.auth.models import Group, Permission
# from rest_framework import serializers

# class PermissionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Permission
#         fields = ['id', 'name', 'codename', 'content_type']

# class GroupSerializer(serializers.ModelSerializer):
#     permissions = PermissionSerializer(many=True, read_only=True)

#     class Meta:
#         model = Group
#         fields = ['id', 'name', 'permissions']



# --- /home/runner/workspace/accounts/serializers/user_serializers.py ---
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

