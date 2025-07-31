
# --- /home/runner/workspace/core/admin.py ---
from django.contrib import admin

# Register your models here.



# --- /home/runner/workspace/core/tests.py ---
from django.test import TestCase

# Create your tests here.



# --- /home/runner/workspace/core/signals.py ---
# core/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from core.models import Empresa
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=Empresa)
def log_empresa_save(sender, instance, created, **kwargs):
    accion = "Creada" if created else "Actualizada"
    # Aquí puedes usar instance.modified_by si guardas usuario en el modelo Empresa
    # O dejar "desconocido" si no tienes
    usuario = getattr(instance, 'modified_by', None)
    usuario_str = usuario.username if usuario else 'desconocido'
    print(f"Empresa {accion}: {instance.razon_social} por usuario {usuario_str} en {now()}")

@receiver(post_delete, sender=Empresa)
def log_empresa_delete(sender, instance, **kwargs):
    print(f"Empresa Eliminada: {instance.razon_social} en {now()}")



# --- /home/runner/workspace/core/apps.py ---
# from django.apps import AppConfig


# class CoreConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'core'
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Importa signals para que se registren
        import core.signals


# --- /home/runner/workspace/core/__init__.py ---
# core/__init__.py

default_app_config = 'core.apps.CoreConfig'


# --- /home/runner/workspace/core/serializers.py ---
# core/serializers.py
from rest_framework import serializers
from core.models import Empresa, Sucursal
import re

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'

    def validate_rfc(self, value):
        # Validación básica de formato RFC mexicano
        pattern = r'^([A-ZÑ&]{3,4}) ?-? ?(\d{2})(\d{2})(\d{2}) ?-? ?([A-Z\d]{3})$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("El RFC no tiene un formato válido")
        # Validar que el RFC sea único
        if Empresa.objects.filter(rfc=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Este RFC ya está registrado")
        return value


class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = '__all__'

# from rest_framework import serializers
# from core.models import Empresa
# import re

# class EmpresaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Empresa
#         fields = '__all__'

#     def validate_rfc(self, value):
#         # Validación básica de formato RFC mexicano
#         pattern = r'^([A-ZÑ&]{3,4}) ?-? ?(\d{2})(\d{2})(\d{2}) ?-? ?([A-Z\d]{3})$'
#         if not re.match(pattern, value):
#             raise serializers.ValidationError("El RFC no tiene un formato válido")
#         # Validar que el RFC sea único
#         if Empresa.objects.filter(rfc=value).exclude(id=self.instance.id if self.instance else None).exists():
#             raise serializers.ValidationError("Este RFC ya está registrado")
#         return value

#     def validate_razon_social(self, value):
#         # Evitar duplicados de razón social
#         if Empresa.objects.filter(razon_social__iexact=value).exclude(id=self.instance.id if self.instance else None).exists():
#             raise serializers.ValidationError("Esta razón social ya está registrada")
#         return value



# --- /home/runner/workspace/core/urls.py ---
# core/urls.py
from rest_framework.routers import DefaultRouter
from core.views import EmpresaViewSet, SucursalViewSet

router = DefaultRouter()
router.register(r'companies', EmpresaViewSet, basename='empresa')
router.register(r'branches', SucursalViewSet, basename='sucursal')


urlpatterns = router.urls


# --- /home/runner/workspace/core/filters.py ---
# core/filters.py

import django_filters
from core.models import Empresa, Sucursal


class EmpresaFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(field_name='nombre', lookup_expr='icontains')
    rfc = django_filters.CharFilter(field_name='rfc', lookup_expr='icontains')
    regimen_fiscal = django_filters.CharFilter(field_name='regimen_fiscal', lookup_expr='icontains')
    creado_en__gte = django_filters.DateTimeFilter(field_name='creado_en', lookup_expr='gte')
    creado_en__lte = django_filters.DateTimeFilter(field_name='creado_en', lookup_expr='lte')

    class Meta:
        model = Empresa
        fields = ['nombre', 'rfc', 'regimen_fiscal', 'creado_en__gte', 'creado_en__lte']


class SucursalFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(field_name='nombre', lookup_expr='icontains')
    empresa = django_filters.NumberFilter(field_name='empresa__id')
    creado_en__gte = django_filters.DateTimeFilter(field_name='creado_en', lookup_expr='gte')
    creado_en__lte = django_filters.DateTimeFilter(field_name='creado_en', lookup_expr='lte')

    class Meta:
        model = Sucursal
        fields = ['nombre', 'empresa', 'creado_en__gte', 'creado_en__lte']



# # core/filters.py
# from django_filters import rest_framework as filters
# from core.models import Empresa

# class EmpresaFilter(filters.FilterSet):
#     rfc = filters.CharFilter(field_name='rfc', lookup_expr='icontains')
#     nombre = filters.CharFilter(field_name='nombre', lookup_expr='icontains')

#     class Meta:
#         model = Empresa
#         fields = ['rfc', 'nombre']



# --- /home/runner/workspace/core/views.py ---
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from core.models import Empresa, Sucursal
from core.serializers import EmpresaSerializer, SucursalSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsSuperAdminOrEmpresaAdmin
from core.filters import EmpresaFilter, SucursalFilter
class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminOrEmpresaAdmin]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmpresaFilter  # usa filtro custom
  
    search_fields = ['nombre', 'rfc', 'domicilio_fiscal', 'regimen_fiscal']
    ordering_fields = ['nombre', 'creado_en', 'actualizado_en']
    ordering = ['nombre']




class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminOrEmpresaAdmin]
    filterset_class = SucursalFilter

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa']
    search_fields = ['nombre', 'direccion']
    ordering_fields = ['nombre', 'creado_en']
    ordering = ['nombre']


# --- /home/runner/workspace/core/models.py ---
# core/models.py

from django.db import models
from django.utils import timezone


class Empresa(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    rfc = models.CharField(max_length=13, unique=True)  # RFC México: 12 o 13 caracteres
    domicilio_fiscal = models.TextField()
    regimen_fiscal = models.CharField(max_length=100)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    razon_social = models.CharField(max_length=255, blank=True, null=True)  # Añadido razon_social



    domicilio_calle = models.CharField(max_length=150)
    domicilio_num_ext = models.CharField(max_length=10, blank=True, null=True)
    domicilio_num_int = models.CharField(max_length=10, blank=True, null=True)
    domicilio_colonia = models.CharField(max_length=100)
    domicilio_municipio = models.CharField(max_length=100)
    domicilio_estado = models.CharField(max_length=100)
    domicilio_pais = models.CharField(max_length=50, default='MEX')
    domicilio_codigo_postal = models.CharField(max_length=10)

    def get_direccion_formateada(self):
        partes = [
            self.domicilio_calle,
            f"Ext. {self.domicilio_num_ext}" if self.domicilio_num_ext else None,
            f"Int. {self.domicilio_num_int}" if self.domicilio_num_int else None,
            self.domicilio_colonia,
            self.domicilio_municipio,
            self.domicilio_estado,
            self.domicilio_pais,
            self.domicilio_codigo_postal,
        ]
        # Eliminar None o vacíos y unir con coma
        return ", ".join(filter(None, partes))
    

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Sucursal(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='sucursales')
    nombre = models.CharField(max_length=150)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    domicilio_calle = models.CharField(max_length=150)
    domicilio_num_ext = models.CharField(max_length=10, blank=True, null=True)
    domicilio_num_int = models.CharField(max_length=10, blank=True, null=True)
    domicilio_colonia = models.CharField(max_length=100)
    domicilio_municipio = models.CharField(max_length=100)
    domicilio_estado = models.CharField(max_length=100)
    domicilio_pais = models.CharField(max_length=50, default='MEX')
    domicilio_codigo_postal = models.CharField(max_length=10)

    def get_direccion_formateada(self):
        partes = [
            self.domicilio_calle,
            f"Ext. {self.domicilio_num_ext}" if self.domicilio_num_ext else None,
            f"Int. {self.domicilio_num_int}" if self.domicilio_num_int else None,
            self.domicilio_colonia,
            self.domicilio_municipio,
            self.domicilio_estado,
            self.domicilio_pais,
            self.domicilio_codigo_postal,
        ]
        # Eliminar None o vacíos y unir con coma
        return ", ".join(filter(None, partes))

    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"
        unique_together = ('empresa', 'nombre')
        ordering = ['empresa', 'nombre']
        indexes = [
            models.Index(fields=['empresa', 'nombre']),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.empresa.nombre})"



# --- /home/runner/workspace/core/migrations/__init__.py ---



# --- /home/runner/workspace/core/migrations/0001_initial.py ---
# Generated by Django 5.2.4 on 2025-07-30 21:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150, unique=True)),
                ('rfc', models.CharField(max_length=13, unique=True)),
                ('domicilio_fiscal', models.TextField()),
                ('regimen_fiscal', models.CharField(max_length=100)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('razon_social', models.CharField(blank=True, max_length=255, null=True)),
                ('domicilio_calle', models.CharField(max_length=150)),
                ('domicilio_num_ext', models.CharField(blank=True, max_length=10, null=True)),
                ('domicilio_num_int', models.CharField(blank=True, max_length=10, null=True)),
                ('domicilio_colonia', models.CharField(max_length=100)),
                ('domicilio_municipio', models.CharField(max_length=100)),
                ('domicilio_estado', models.CharField(max_length=100)),
                ('domicilio_pais', models.CharField(default='MEX', max_length=50)),
                ('domicilio_codigo_postal', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name': 'Empresa',
                'verbose_name_plural': 'Empresas',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Sucursal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('domicilio_calle', models.CharField(max_length=150)),
                ('domicilio_num_ext', models.CharField(blank=True, max_length=10, null=True)),
                ('domicilio_num_int', models.CharField(blank=True, max_length=10, null=True)),
                ('domicilio_colonia', models.CharField(max_length=100)),
                ('domicilio_municipio', models.CharField(max_length=100)),
                ('domicilio_estado', models.CharField(max_length=100)),
                ('domicilio_pais', models.CharField(default='MEX', max_length=50)),
                ('domicilio_codigo_postal', models.CharField(max_length=10)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sucursales', to='core.empresa')),
            ],
            options={
                'verbose_name': 'Sucursal',
                'verbose_name_plural': 'Sucursales',
                'ordering': ['empresa', 'nombre'],
                'indexes': [models.Index(fields=['empresa', 'nombre'], name='core_sucurs_empresa_61cae1_idx')],
                'unique_together': {('empresa', 'nombre')},
            },
        ),
    ]



# --- /home/runner/workspace/core/middleware/auditoria.py ---
# core/middleware/auditoria.py

from accounts.signals import set_audit_user

class AuditoriaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            set_audit_user(request.user)
        response = self.get_response(request)
        return response


# --- /home/runner/workspace/core/middleware/__init__.py ---



# --- /home/runner/workspace/core/api/__init__.py ---



# --- /home/runner/workspace/core/api/auth_viewset.py ---
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse
from rest_framework import viewsets

@extend_schema_view(
    post=extend_schema(
        summary="Login",
        description="Autenticación con JWT",
        responses={
            200: OpenApiResponse(description="Login exitoso"),
            400: OpenApiResponse(description="Datos inválidos"),
            401: OpenApiResponse(description="Credenciales incorrectas"),
            500: OpenApiResponse(description="Error interno"),
        },
    ),
    get=extend_schema(
        summary="Ver perfil",
        description="Datos del usuario autenticado",
        responses={
            200: OpenApiResponse(description="Datos del usuario"),
            401: OpenApiResponse(description="Token inválido o no enviado"),
        },
    ),
)
class AuthViewSet(viewsets.ViewSet):
    pass



# --- /home/runner/workspace/core/api/urls.py ---
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .auth_viewset import AuthViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
]

