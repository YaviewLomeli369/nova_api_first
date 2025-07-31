
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



# --- /home/runner/workspace/inventario/filters.py ---
import django_filters
from inventario.models import Producto
from django.db.models import Q
from django_filters import rest_framework as filters
from inventario.models import Inventario

class ProductoFilter(filters.FilterSet):
    nombre = filters.CharFilter(field_name='nombre', lookup_expr='icontains', label='Nombre contiene')
    descripcion = filters.CharFilter(field_name='descripcion', lookup_expr='icontains', label='Descripción contiene')
    precio_min = filters.NumberFilter(field_name='precio_venta', lookup_expr='gte', label='Precio mínimo')
    precio_max = filters.NumberFilter(field_name='precio_venta', lookup_expr='lte', label='Precio máximo')
    stock_min = filters.NumberFilter(field_name='stock', lookup_expr='gte', label='Stock mínimo')
    stock_max = filters.NumberFilter(field_name='stock', lookup_expr='lte', label='Stock máximo')
    fecha_vencimiento_desde = filters.DateFilter(field_name='fecha_vencimiento', lookup_expr='gte')
    fecha_vencimiento_hasta = filters.DateFilter(field_name='fecha_vencimiento', lookup_expr='lte')
    activo = filters.BooleanFilter(field_name='activo')
    categoria = filters.NumberFilter(field_name='categoria_id')
    proveedor = filters.NumberFilter(field_name='proveedor_id')

    class Meta:
        model = Producto
        fields = []



class InventarioFilter(django_filters.FilterSet):
    producto = django_filters.CharFilter(field_name='producto__nombre', lookup_expr='icontains', label="Nombre del producto")
    sucursal = django_filters.NumberFilter(field_name='sucursal__id', label="ID de sucursal")
    cantidad_min = django_filters.NumberFilter(field_name='cantidad', lookup_expr='gte', label="Cantidad mínima")
    cantidad_max = django_filters.NumberFilter(field_name='cantidad', lookup_expr='lte', label="Cantidad máxima")

    class Meta:
        model = Inventario
        fields = ['producto', 'sucursal', 'cantidad_min', 'cantidad_max']


# --- /home/runner/workspace/inventario/models.py ---
# inventario/models.py

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class ClaveSATUnidad(models.Model):
    clave = models.CharField(max_length=10, unique=True)  # ej: "H87"
    descripcion = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Clave SAT Unidad"
        verbose_name_plural = "Claves SAT Unidades"
        ordering = ['clave']

    def __str__(self):
        return f"{self.clave} - {self.descripcion}"

class ClaveSATProducto(models.Model):
    clave = models.CharField(max_length=20, unique=True)  # ej: "01010101"
    descripcion = models.CharField(max_length=255)
    unidad = models.ForeignKey(ClaveSATUnidad, on_delete=models.PROTECT, related_name='claves_productos')

    class Meta:
        verbose_name = "Clave SAT Producto"
        verbose_name_plural = "Claves SAT Productos"
        ordering = ['clave']

    def __str__(self):
        return f"{self.clave} - {self.descripcion} ({self.unidad.clave})"




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

    # En vez de usar unidad_medida de texto libre, se apunta a clave SAT unidad
    unidad_medida = models.ForeignKey(
        ClaveSATUnidad,
        on_delete=models.PROTECT,
        related_name='productos',
        null=True,
        blank=True,
        help_text="Clave SAT de unidad de medida"
    )

    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

    # Clave SAT del producto (por ejemplo para facturación electrónica)
    clave_sat = models.ForeignKey(
        ClaveSATProducto,
        on_delete=models.PROTECT,
        related_name='productos',
        null=True,
        blank=True,
        help_text="Clave SAT del producto o servicio"
    )

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
        unique_together = ('producto', 'sucursal', 'lote', 'fecha_vencimiento')
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


# --- /home/runner/workspace/inventario/migrations/__init__.py ---



# --- /home/runner/workspace/inventario/migrations/0001_initial.py ---
# Generated by Django 5.2.4 on 2025-07-30 21:47

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
            name='ClaveSATUnidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clave', models.CharField(max_length=10, unique=True)),
                ('descripcion', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Clave SAT Unidad',
                'verbose_name_plural': 'Claves SAT Unidades',
                'ordering': ['clave'],
            },
        ),
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
            name='ClaveSATProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clave', models.CharField(max_length=20, unique=True)),
                ('descripcion', models.CharField(max_length=255)),
                ('unidad', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='claves_productos', to='inventario.clavesatunidad')),
            ],
            options={
                'verbose_name': 'Clave SAT Producto',
                'verbose_name_plural': 'Claves SAT Productos',
                'ordering': ['clave'],
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
                ('precio_compra', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_venta', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock_minimo', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('activo', models.BooleanField(default=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='inventario.categoria')),
                ('clave_sat', models.ForeignKey(blank=True, help_text='Clave SAT del producto o servicio', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='productos', to='inventario.clavesatproducto')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='core.empresa')),
                ('unidad_medida', models.ForeignKey(blank=True, help_text='Clave SAT de unidad de medida', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='productos', to='inventario.clavesatunidad')),
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
        migrations.AlterUniqueTogether(
            name='inventario',
            unique_together={('producto', 'sucursal', 'lote', 'fecha_vencimiento')},
        ),
    ]



# --- /home/runner/workspace/inventario/views/__init__.py ---



# --- /home/runner/workspace/inventario/views/producto.py ---
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from inventario.models import Producto
from inventario.serializers import ProductoSerializer
from inventario.filters import ProductoFilter
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions

class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

    queryset = Producto.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductoFilter

    search_fields = ['codigo', 'nombre', 'descripcion', 'codigo_barras', 'lote']
    ordering_fields = ['nombre', 'precio_venta', 'stock', 'fecha_vencimiento']
    ordering = ['nombre']

    def get_queryset(self):
        return Producto.objects.filter(empresa=self.request.user.empresa)






# --- /home/runner/workspace/inventario/views/categoria.py ---
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from inventario.models import Categoria
from inventario.serializers import CategoriaSerializer

from accounts.permissions import IsAdminOrReadOnly

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        # Multitenencia: cada usuario solo ve categorías de su empresa
        user = self.request.user
        return self.queryset.filter(empresa=user.empresa)

# from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated
# from inventario.models import Categoria
# from inventario.serializers import CategoriaSerializer

# from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions

# class CategoriaViewSet(viewsets.ModelViewSet):
#     queryset = Categoria.objects.all()
#     serializer_class = CategoriaSerializer
#     permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

#     def get_queryset(self):
#         # Multitenencia: cada usuario solo ve categorías de su empresa
#         user = self.request.user
#         return self.queryset.filter(empresa=user.empresa)





# --- /home/runner/workspace/inventario/views/inventario.py ---
# inventario/views/inventario.py

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from inventario.models import Inventario
from inventario.serializers import InventarioSerializer
from inventario.filters import InventarioFilter
from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions

class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.select_related('producto', 'sucursal')
    serializer_class = InventarioSerializer
    permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = InventarioFilter
    search_fields = ['producto__nombre', 'sucursal__nombre']  # Búsqueda libre
    ordering_fields = ['cantidad', 'producto__nombre', 'sucursal__nombre']
    ordering = ['-cantidad']  # Orden por defecto

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(producto__empresa=user.empresa)

# from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated
# from inventario.models import Inventario
# from inventario.serializers import InventarioSerializer

# from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions

# class InventarioViewSet(viewsets.ModelViewSet):
#     queryset = Inventario.objects.select_related('producto', 'sucursal')
#     serializer_class = InventarioSerializer
#     permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

#     def get_queryset(self):
#         user = self.request.user
#         return self.queryset.filter(producto__empresa=user.empresa)



# --- /home/runner/workspace/inventario/views/movimiento.py ---
from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from inventario.models import MovimientoInventario, Inventario
from inventario.serializers import MovimientoInventarioSerializer

from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions
from accounts.models import Auditoria  # 👈 Auditoría personalizada


class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

    def get_queryset(self):
        user = self.request.user
        return MovimientoInventario.objects.filter(inventario__producto__empresa=user.empresa).order_by('-fecha')

    def perform_create(self, serializer):
        movimiento = serializer.save(usuario=self.request.user)
        inventario = movimiento.inventario
        cantidad = movimiento.cantidad

        if movimiento.tipo_movimiento == 'salida':
            if cantidad > inventario.cantidad:
                raise serializers.ValidationError("No hay suficiente inventario para esta salida.")
            inventario.cantidad -= cantidad

        elif movimiento.tipo_movimiento == 'entrada':
            inventario.cantidad += cantidad

        elif movimiento.tipo_movimiento == 'ajuste':
            # Lógica personalizada según sea necesario
            pass

        inventario.full_clean()
        inventario.save()

        # 📝 Auditoría
        Auditoria.objects.create(
            usuario=self.request.user,
            accion='crear',
            tabla_afectada='MovimientoInventario',
            registro_afectado=f"ID: {movimiento.id}, Tipo: {movimiento.tipo_movimiento}, Cantidad: {movimiento.cantidad}"
        )

    def perform_update(self, serializer):
        movimiento = serializer.save()

        # No se actualiza inventario directamente desde aquí (recomendado)
        # Pero puedes auditar igual:
        Auditoria.objects.create(
            usuario=self.request.user,
            accion='actualizar',
            tabla_afectada='MovimientoInventario',
            registro_afectado=f"ID: {movimiento.id}, Tipo: {movimiento.tipo_movimiento}, Cantidad: {movimiento.cantidad}"
        )

    def perform_destroy(self, instance):
        # Guarda info antes de borrar
        info = f"ID: {instance.id}, Tipo: {instance.tipo_movimiento}, Cantidad: {instance.cantidad}"
        instance.delete()

        Auditoria.objects.create(
            usuario=self.request.user,
            accion='eliminar',
            tabla_afectada='MovimientoInventario',
            registro_afectado=info
        )






# from rest_framework import viewsets, serializers
# from rest_framework.permissions import IsAuthenticated
# from inventario.models import MovimientoInventario, Inventario
# from inventario.serializers import MovimientoInventarioSerializer

# from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions

# class MovimientoInventarioViewSet(viewsets.ModelViewSet):
#     serializer_class = MovimientoInventarioSerializer
#     permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

#     def get_queryset(self):
#         user = self.request.user
#         return MovimientoInventario.objects.filter(inventario__producto__empresa=user.empresa).order_by('-fecha')

#     def perform_create(self, serializer):
#         movimiento = serializer.save(usuario=self.request.user)
#         inventario = movimiento.inventario
#         cantidad = movimiento.cantidad

#         if movimiento.tipo_movimiento == 'salida':
#             if cantidad > inventario.cantidad:
#                 raise serializers.ValidationError("No hay suficiente inventario para esta salida.")
#             inventario.cantidad -= cantidad

#         elif movimiento.tipo_movimiento == 'entrada':
#             inventario.cantidad += cantidad

#         elif movimiento.tipo_movimiento == 'ajuste':
#             # Puedes definir reglas personalizadas si se desea
#             pass

#         # Validación final y guardado
#         inventario.full_clean()
#         inventario.save()



# # from rest_framework import viewsets
# # from rest_framework.permissions import IsAuthenticated
# # from inventario.models import MovimientoInventario
# # from inventario.serializers import MovimientoInventarioSerializer

# # from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions

# # class MovimientoInventarioViewSet(viewsets.ModelViewSet):
# #     serializer_class = MovimientoInventarioSerializer
# #     permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

# #     def get_queryset(self):
# #         user = self.request.user
# #         return MovimientoInventario.objects.filter(producto__empresa=user.empresa).order_by('-fecha')

# # # inventario/views/movimiento.py

# # from rest_framework import viewsets
# # from inventario.models import MovimientoInventario
# # from inventario.serializers import MovimientoInventarioSerializer

# # class MovimientoInventarioViewSet(viewsets.ModelViewSet):  # ✅ debe ser ModelViewSet
# #     queryset = MovimientoInventario.objects.all()
# #     serializer_class = MovimientoInventarioSerializer



# --- /home/runner/workspace/inventario/views/batches.py ---
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from inventario.models import Inventario
from inventario.serializers import InventarioSerializer, BatchSerializer
from django.utils import timezone

from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions
from datetime import timedelta

class BatchView(APIView):
    permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

    def get(self, request):
        user = request.user
        hoy = timezone.now().date()
        alerta_hasta = hoy + timedelta(days=30)

        inventarios = Inventario.objects.select_related('producto').filter(
            producto__empresa=user.empresa,
            fecha_vencimiento__isnull=False,
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=alerta_hasta
        ).order_by('fecha_vencimiento')

        serializer = BatchSerializer(inventarios, many=True)
        return Response(serializer.data)






# # inventario/views/batches.py

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from inventario.models import Inventario
# from inventario.serializers import InventarioSerializer
# from django.utils import timezone

# class BatchView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         empresa = request.user.empresa
#         hoy = timezone.now().date()
#         inventarios = Inventario.objects.filter(
#             producto__empresa=empresa,
#             fecha_vencimiento__isnull=False
#         ).order_by('fecha_vencimiento')

#         serializer = InventarioSerializer(inventarios, many=True)
#         return Response(serializer.data)



# --- /home/runner/workspace/inventario/views/stock_alerts.py ---
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import F

from inventario.models import Producto
from inventario.serializers import ProductoSerializer

from accounts.permissions import IsSuperAdminOrEmpresaAdmin, IsInventario
from django.db.models import Sum

# inventario/views/stock_alerts.py (o donde prefieras)

from datetime import date, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# from inventario.models import Batch
from inventario.serializers import BatchSerializer

from accounts.permissions import IsSuperAdminOrEmpresaAdmin, IsInventario

class ExpirationAlertView(APIView):
    permission_classes = [IsAuthenticated & (IsSuperAdminOrEmpresaAdmin | IsInventario)]

    def get(self, request):
        empresa = request.user.empresa
        hoy = date.today()
        alerta_hasta = hoy + timedelta(days=30)  # Próximos 30 días

        lotes_proximos_a_vencer = Batch.objects.filter(
            empresa=empresa,
            activo=True,
            fecha_vencimiento__lte=alerta_hasta,
            fecha_vencimiento__gte=hoy
        ).order_by('fecha_vencimiento')

        serializer = BatchSerializer(lotes_proximos_a_vencer, many=True)
        return Response(serializer.data)

class StockAlertView(APIView):
    permission_classes = [IsAuthenticated & (IsSuperAdminOrEmpresaAdmin | IsInventario)]

    def get(self, request):
        empresa = request.user.empresa
        productos_alerta = Producto.objects.filter(
            empresa=empresa,
            activo=True
        ).annotate(
            stock_total=Sum('inventarios__cantidad')
        ).filter(
            stock_total__lt=F('stock_minimo')
        )

        serializer = ProductoSerializer(productos_alerta, many=True)
        return Response(serializer.data)



# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.db.models import F

# from inventario.models import Producto
# from inventario.serializers import ProductoSerializer

# from accounts.permissions import IsSuperAdminOrEmpresaAdmin, IsInventario

# class StockAlertView(APIView):
#     permission_classes = [IsAuthenticated & (IsSuperAdminOrEmpresaAdmin | IsInventario)]

#     def get(self, request):
#         empresa = request.user.empresa
#         productos_alerta = Producto.objects.filter(
#             empresa=empresa,
#             activo=True,
#             inventarios__cantidad__lt=F('stock_minimo')
#         ).distinct()

#         serializer = ProductoSerializer(productos_alerta, many=True)
#         return Response(serializer.data)



# --- /home/runner/workspace/inventario/serializers/inventario_serializers.py ---
from rest_framework import serializers
from inventario.models import Inventario

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



# --- /home/runner/workspace/inventario/serializers/categoria_serializers.py ---
from rest_framework import serializers
from inventario.models import Categoria

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ['id']



# --- /home/runner/workspace/inventario/serializers/batch_serializer.py ---
# inventario/serializers.py
from rest_framework import serializers
from inventario.models import Inventario

class BatchSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = Inventario
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'fecha_vencimiento', 'ubicacion']



# --- /home/runner/workspace/inventario/serializers/__init__.py ---
from .categoria_serializers import CategoriaSerializer
from .producto_serializers import ProductoSerializer
from .inventario_serializers import InventarioSerializer
from .movimiento_inventario_serializers import MovimientoInventarioSerializer
from .batch_serializer import BatchSerializer

__all__ = [
    'CategoriaSerializer',
    'ProductoSerializer',
    'InventarioSerializer',
    'MovimientoInventarioSerializer',
    'BatchSerializer',
]


# --- /home/runner/workspace/inventario/serializers/movimiento_inventario_serializers.py ---
from rest_framework import serializers
from inventario.models import MovimientoInventario

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

        if tipo == 'entrada':
            producto.stock += cantidad
        elif tipo == 'salida':
            producto.stock -= cantidad
        elif tipo == 'ajuste':
            producto.stock = cantidad  # Ajuste directo

        producto.save()
        return super().create(validated_data)



# --- /home/runner/workspace/inventario/serializers/producto_serializers.py ---
from rest_framework import serializers
from inventario.models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'empresa', 'codigo', 'nombre', 'descripcion', 'unidad_medida', 'categoria',
            'categoria_nombre', 'precio_compra', 'precio_venta', 'stock_minimo', 'activo', 'clave_sat'
        ]
        read_only_fields = ['id']

    def validate(self, data):
        precio_venta = data.get('precio_venta', getattr(self.instance, 'precio_venta', None))
        precio_compra = data.get('precio_compra', getattr(self.instance, 'precio_compra', None))

        if precio_venta is not None and precio_compra is not None:
            if precio_venta < precio_compra:
                raise serializers.ValidationError("El precio de venta no puede ser menor que el de compra.")

        return data


