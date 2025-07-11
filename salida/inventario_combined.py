
# --- /home/runner/workspace/inventario/__init__.py ---



# --- /home/runner/workspace/inventario/admin.py ---
from django.contrib import admin

# Register your models here.



# --- /home/runner/workspace/inventario/apps.py ---
from django.apps import AppConfig


class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventario'



# --- /home/runner/workspace/inventario/tests.py ---
from django.test import TestCase

# Create your tests here.



# --- /home/runner/workspace/inventario/views.py ---
from django.shortcuts import render

# Create your views here.



# --- /home/runner/workspace/inventario/models.py ---
# inventario/models.py

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Categoria(models.Model):
    empresa = models.ForeignKey('core.Empresa', on_delete=models.CASCADE, related_name='categorias')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['empresa', 'nombre']),
        ]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    empresa = models.ForeignKey('core.Empresa', on_delete=models.CASCADE, related_name='productos')
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.CharField(max_length=50)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

    def clean(self):
        if self.precio_venta < self.precio_compra:
            raise ValidationError("El precio de venta no puede ser menor que el precio de compra.")
        if self.precio_compra < 0 or self.precio_venta < 0:
            raise ValidationError("Los precios no pueden ser negativos.")
        if self.stock_minimo < 0:
            raise ValidationError("El stock mínimo no puede ser negativo.")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['empresa', 'codigo']),
            models.Index(fields=['categoria']),
        ]

    def __str__(self):
        return self.nombre


class Inventario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='inventarios')
    sucursal = models.ForeignKey('core.Sucursal', on_delete=models.CASCADE, related_name='inventarios')
    lote = models.CharField(max_length=100, blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        if self.cantidad < 0:
            raise ValidationError("La cantidad en inventario no puede ser negativa.")
        if self.fecha_vencimiento and self.fecha_vencimiento < timezone.now().date():
            raise ValidationError("La fecha de vencimiento no puede estar en el pasado.")


    class Meta:
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"
        indexes = [
            models.Index(fields=['producto', 'sucursal']),
            models.Index(fields=['fecha_vencimiento']),
        ]
        ordering = ['producto']

    def __str__(self):
        return f"{self.producto.nombre} - {self.sucursal.nombre}"


class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    ]

    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.DecimalField(max_digits=14, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey('accounts.Usuario', on_delete=models.PROTECT, related_name='movimientos_inventario')

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['inventario', 'fecha']),
            models.Index(fields=['tipo_movimiento']),
        ]

    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} - {self.cantidad} unidades - {self.fecha}"



# --- /home/runner/workspace/inventario/serializers.py ---
# inventario/serializers.py

from rest_framework import serializers
from .models import Categoria, Producto, Inventario, MovimientoInventario

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ['id']


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'empresa', 'codigo', 'nombre', 'descripcion', 'unidad_medida', 'categoria',
            'categoria_nombre', 'precio_compra', 'precio_venta', 'stock_minimo', 'activo'
        ]
        read_only_fields = ['id']


    def validate(self, data):
        precio_venta = data.get('precio_venta', getattr(self.instance, 'precio_venta', None))
        precio_compra = data.get('precio_compra', getattr(self.instance, 'precio_compra', None))

        # Solo validar si ambos valores están disponibles
        if precio_venta is not None and precio_compra is not None:
            if precio_venta < precio_compra:
                raise serializers.ValidationError("El precio de venta no puede ser menor que el de compra.")

        return data

    # def validate(self, data):
    #     if data['precio_venta'] < data['precio_compra']:
    #         raise serializers.ValidationError("El precio de venta no puede ser menor que el de compra.")
    #     return data


class InventarioSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)

    class Meta:
        model = Inventario
        fields = [
            'id', 'producto', 'producto_nombre', 'sucursal', 'sucursal_nombre',
            'lote', 'fecha_vencimiento', 'cantidad'
        ]
        read_only_fields = ['id']

    def validate_cantidad(self, value):
        if value < 0:
            raise serializers.ValidationError("La cantidad no puede ser negativa.")
        return value


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoInventario
        fields = '__all__'

    def validate(self, data):
        producto = data['producto']
        tipo = data['tipo']
        cantidad = data['cantidad']

        if tipo == 'salida' and producto.stock < cantidad:
            raise serializers.ValidationError("Stock insuficiente para salida.")

        return data

    def create(self, validated_data):
        producto = validated_data['producto']
        tipo = validated_data['tipo']
        cantidad = validated_data['cantidad']

        # Actualiza el stock
        if tipo == 'entrada':
            producto.stock += cantidad
        elif tipo == 'salida':
            producto.stock -= cantidad
        elif tipo == 'ajuste':
            producto.stock = cantidad  # Ajuste directo

        producto.save()
        return super().create(validated_data)


# --- /home/runner/workspace/inventario/urls.py ---
from rest_framework.routers import DefaultRouter
from django.urls import path
from inventario.views.producto import ProductoViewSet
from inventario.views.categoria import CategoriaViewSet  # Asumido: Vista para categorías
from inventario.views.inventario import InventarioViewSet
from inventario.views.movimiento import MovimientoInventarioViewSet
from inventario.views.stock_alerts import StockAlertView
from inventario.views.batches import BatchView

# Crear un enrutador para el registro de vistas (ViewSets)
router = DefaultRouter()
router.register(r'products', ProductoViewSet, basename='product')  # Endpoint para productos
router.register(r'categories', CategoriaViewSet, basename='category')  # Endpoint para categorías
router.register(r'inventory', InventarioViewSet, basename='inventory')  # Endpoint para inventario
router.register(r'movements', MovimientoInventarioViewSet, basename='inventory-movement')  # Endpoint para movimientos

# Lista de URLs que combinan las rutas generadas por el router con otras rutas personalizadas
urlpatterns = router.urls + [
    # Rutas personalizadas adicionales (las nuevas que mencionabas)
    path('stock-alerts/', StockAlertView.as_view(), name='stock-alerts'),  # Rutas para las alertas de stock
    path('batches/', BatchView.as_view(), name='inventory-batches'),  # Rutas para lotes de inventario
]


# from rest_framework.routers import DefaultRouter
# from django.urls import path
# from inventario.views.producto import ProductoViewSet
# from inventario.views.inventario import InventarioViewSet
# from inventario.views.movimiento import MovimientoInventarioViewSet
# from inventario.views.stock_alerts import StockAlertView
# from inventario.views.batches import BatchView

# # Crear un enrutador para el registro de vistas (ViewSets)
# router = DefaultRouter()
# router.register(r'products', ProductoViewSet, basename='product')
# router.register(r'inventory', InventarioViewSet, basename='inventory')
# router.register(r'movements', MovimientoInventarioViewSet, basename='inventory-movement')


# # Lista de URLs que combinan las rutas generadas por el router con otras rutas personalizadas
# urlpatterns = router.urls + [
#     # Rutas personalizadas adicionales
#     path('inventory/stock-alerts/', StockAlertView.as_view(), name='stock-alerts'),
#     path('inventory/batches/', BatchView.as_view(), name='inventory-batches'),
# ]
# # from rest_framework.routers import DefaultRouter
# # from django.urls import path
# # from inventario.views.producto import ProductoViewSet
# # from inventario.views.inventario import InventarioViewSet
# # from inventario.views.movimiento import MovimientoInventarioViewSet
# # from inventario.views.stock_alerts import StockAlertView
# # from inventario.views.batches import BatchView

# # # Crear un enrutador para el registro de vistas (ViewSets)
# # router = DefaultRouter()
# # router.register(r'products', ProductoViewSet, basename='product')
# # router.register(r'inventory', InventarioViewSet, basename='inventory')
# # router.register(r'inventory/movements', MovimientoInventarioViewSet, basename='inventory-movement')


# # # Lista de URLs que combinan las rutas generadas por el router con otras rutas personalizadas
# # urlpatterns = router.urls + [
# #     # Rutas personalizadas adicionales
# #     path('inventory/stock-alerts/', StockAlertView.as_view(), name='stock-alerts'),
# #     path('inventory/batches/', BatchView.as_view(), name='inventory-batches'),
# # ]
# # # inventario/urls.py

# # from rest_framework.routers import DefaultRouter
# # from django.urls import path
# # from inventario.views.producto import ProductoViewSet
# # from inventario.views.inventario import InventarioViewSet
# # from inventario.views.movimiento import MovimientoInventarioViewSet
# # from inventario.views.stock_alerts import StockAlertView
# # from inventario.views.batches import BatchView

# # router = DefaultRouter()
# # router.register(r'products', ProductoViewSet, basename='product')
# # router.register(r'inventory', InventarioViewSet, basename='inventory')
# # router.register(r'inventory/movements', MovimientoInventarioViewSet, basename='inventory-movement')

# # urlpatterns = router.urls + [
# #     path('inventory/stock-alerts/', StockAlertView.as_view(), name='stock-alerts'),
# #     path('inventory/batches/', BatchView.as_view(), name='inventory-batches'),
# # ]


# # inventario

# # 🔹 4. /movimientos/ → MovimientoInventarioViewSet
# # Método	Ruta	Acción
# # GET	/api/inventario/movimientos/	Listar movimientos
# # POST	/api/inventario/movimientos/	Crear nuevo movimiento
# # GET	/api/inventario/movimientos/{id}/	Ver detalle de movimiento
# # PUT	/api/inventario/movimientos/{id}/	❌ No recomendado (stock ya movido)
# # PATCH	/api/inventario/movimientos/{id}/	❌ Idem anterior
# # DELETE	/api/inventario/movimientos/{id}/	❌ No recomendado (auditoría)

# # # inventario/urls.py

# # from rest_framework.routers import DefaultRouter
# # from django.urls import path, include

# # from inventario.views.categoria import CategoriaViewSet
# # from inventario.views.producto import ProductoViewSet
# # from inventario.views.inventario import InventarioViewSet
# # from inventario.views.movimiento import MovimientoInventarioViewSet

# # router = DefaultRouter()
# # router.register(r'categorias', CategoriaViewSet, basename='categoria')
# # router.register(r'productos', ProductoViewSet, basename='producto')
# # router.register(r'inventarios', InventarioViewSet, basename='inventario')
# # router.register(r'movimientos', MovimientoInventarioViewSet, basename='movimiento-inventario')

# # urlpatterns = [
# #     path('', include(router.urls)),
# # ]



# --- /home/runner/workspace/inventario/migrations/__init__.py ---



# --- /home/runner/workspace/inventario/migrations/0001_initial.py ---
# Generated by Django 5.2.4 on 2025-07-04 22:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categorias', to='core.empresa')),
            ],
            options={
                'verbose_name': 'Categoría',
                'verbose_name_plural': 'Categorías',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Inventario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lote', models.CharField(blank=True, max_length=100, null=True)),
                ('fecha_vencimiento', models.DateField(blank=True, null=True)),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventarios', to='core.sucursal')),
            ],
            options={
                'verbose_name': 'Inventario',
                'verbose_name_plural': 'Inventarios',
                'ordering': ['producto'],
            },
        ),
        migrations.CreateModel(
            name='MovimientoInventario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_movimiento', models.CharField(choices=[('entrada', 'Entrada'), ('salida', 'Salida'), ('ajuste', 'Ajuste')], max_length=10)),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=14)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('inventario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movimientos', to='inventario.inventario')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='movimientos_inventario', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Movimiento de Inventario',
                'verbose_name_plural': 'Movimientos de Inventario',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=50, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('unidad_medida', models.CharField(max_length=50)),
                ('precio_compra', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_venta', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock_minimo', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('activo', models.BooleanField(default=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='inventario.categoria')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='core.empresa')),
            ],
            options={
                'verbose_name': 'Producto',
                'verbose_name_plural': 'Productos',
                'ordering': ['nombre'],
            },
        ),
        migrations.AddField(
            model_name='inventario',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventarios', to='inventario.producto'),
        ),
        migrations.AddIndex(
            model_name='categoria',
            index=models.Index(fields=['empresa', 'nombre'], name='inventario__empresa_ef6442_idx'),
        ),
        migrations.AddIndex(
            model_name='movimientoinventario',
            index=models.Index(fields=['inventario', 'fecha'], name='inventario__inventa_c73e96_idx'),
        ),
        migrations.AddIndex(
            model_name='movimientoinventario',
            index=models.Index(fields=['tipo_movimiento'], name='inventario__tipo_mo_89d562_idx'),
        ),
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(fields=['empresa', 'codigo'], name='inventario__empresa_800e68_idx'),
        ),
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(fields=['categoria'], name='inventario__categor_32aa4f_idx'),
        ),
        migrations.AddIndex(
            model_name='inventario',
            index=models.Index(fields=['producto', 'sucursal'], name='inventario__product_1e48f1_idx'),
        ),
        migrations.AddIndex(
            model_name='inventario',
            index=models.Index(fields=['fecha_vencimiento'], name='inventario__fecha_v_7b1ec0_idx'),
        ),
    ]



# --- /home/runner/workspace/inventario/views/categoria.py ---
from rest_framework import viewsets
from inventario.models import Categoria
from inventario.serializers import CategoriaSerializer
from rest_framework.permissions import IsAuthenticated

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(empresa=self.request.user.empresa)



# --- /home/runner/workspace/inventario/views/producto.py ---
from rest_framework import viewsets
from inventario.models import Producto
from inventario.serializers import ProductoSerializer
from rest_framework.permissions import IsAuthenticated

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(empresa=self.request.user.empresa)



# --- /home/runner/workspace/inventario/views/inventario.py ---
from rest_framework import viewsets
from inventario.models import Inventario
from inventario.serializers import InventarioSerializer
from rest_framework.permissions import IsAuthenticated

class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.select_related('producto', 'sucursal')
    serializer_class = InventarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(producto__empresa=self.request.user.empresa)



# --- /home/runner/workspace/inventario/views/__init__.py ---



# --- /home/runner/workspace/inventario/views/stock_alerts.py ---
# inventario/views/stock_alerts.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from inventario.models import Producto
from inventario.serializers import ProductoSerializer
from django.db.models import F

class StockAlertView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa = request.user.empresa
        productos_alerta = Producto.objects.filter(
            empresa=empresa,
            activo=True,
            inventarios__cantidad__lt=F('stock_minimo')
        ).distinct()

        serializer = ProductoSerializer(productos_alerta, many=True)
        return Response(serializer.data)



# --- /home/runner/workspace/inventario/views/batches.py ---
# inventario/views/batches.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from inventario.models import Inventario
from inventario.serializers import InventarioSerializer
from django.utils import timezone

class BatchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa = request.user.empresa
        hoy = timezone.now().date()
        inventarios = Inventario.objects.filter(
            producto__empresa=empresa,
            fecha_vencimiento__isnull=False
        ).order_by('fecha_vencimiento')

        serializer = InventarioSerializer(inventarios, many=True)
        return Response(serializer.data)



# --- /home/runner/workspace/inventario/views/movimiento.py ---
# inventario/views/movimiento.py

from rest_framework import viewsets
from inventario.models import MovimientoInventario
from inventario.serializers import MovimientoInventarioSerializer

class MovimientoInventarioViewSet(viewsets.ModelViewSet):  # ✅ debe ser ModelViewSet
    queryset = MovimientoInventario.objects.all()
    serializer_class = MovimientoInventarioSerializer


