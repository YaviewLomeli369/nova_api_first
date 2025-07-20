
# --- /home/runner/workspace/compras/__init__.py ---



# --- /home/runner/workspace/compras/admin.py ---
from django.contrib import admin

# Register your models here.



# --- /home/runner/workspace/compras/apps.py ---
from django.apps import AppConfig


class ComprasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'compras'



# --- /home/runner/workspace/compras/urls.py ---
from compras.views.proveedor_views import ProveedorViewSet


from rest_framework import routers
from django.urls import path, include
from compras.views.compra_views import CompraViewSet, ReceivePurchase , CompraReceiveView, CompraRecepcionParcialAPIView, CompraCancelarAPIView

router = routers.DefaultRouter()
router.register(r'providers', ProveedorViewSet, basename='proveedor')
router.register(r'purchases', CompraViewSet, basename='purchases')

urlpatterns = [
    path('', include(router.urls)),
    # path('purchases/<int:id>/receive/', ReceivePurchase.as_view(), name='receive_purchase')
    path('purchases/<int:pk>/receive/', CompraReceiveView.as_view(), name='compra-receive'),
    path('purchases/<int:pk>/partial-reception/', CompraRecepcionParcialAPIView.as_view(), name='compra-recepcion-parcial'),
    path('purchases/<int:pk>/cancelar/', CompraCancelarAPIView.as_view(), name='cancelar_compra'),
]


# --- /home/runner/workspace/compras/filters.py ---
# compras/filters.py

import django_filters
from compras.models import Compra

class CompraFilter(django_filters.FilterSet):
    # Rango de fechas
    fecha_min = django_filters.DateFilter(field_name='fecha', lookup_expr='gte')
    fecha_max = django_filters.DateFilter(field_name='fecha', lookup_expr='lte')

    # Rango de totales
    total_min = django_filters.NumberFilter(field_name='total', lookup_expr='gte')
    total_max = django_filters.NumberFilter(field_name='total', lookup_expr='lte')

    # Filtro exacto por nombre de producto
    nombre_producto = django_filters.CharFilter(method='filter_nombre_producto')

    # Filtros por ID o múltiples productos
    producto_id = django_filters.NumberFilter(field_name='detalles__producto__id')
    producto_id__in = django_filters.BaseInFilter(field_name='detalles__producto__id', lookup_expr='in')

    class Meta:
        model = Compra
        fields = ['empresa', 'proveedor', 'estado']

    def filter_nombre_producto(self, queryset, name, value):
        return queryset.filter(detalles__producto__nombre__icontains=value).distinct()


# --- /home/runner/workspace/compras/models.py ---
# compras/models.py
from django.db import models
from django.utils import timezone
from accounts.models import Usuario, Empresa
from inventario.models import Producto
from django.core.exceptions import ValidationError
from django.utils import timezone

class Proveedor(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='proveedores')
    nombre = models.CharField(max_length=255)
    rfc = models.CharField(max_length=13)
    correo = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        unique_together = ('empresa', 'rfc')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# class Compra(models.Model):
#     ESTADO_CHOICES = [
#         ('pendiente', 'Pendiente'),  # La compra está pendiente de ser recibida
#         ('parcial', 'Parcial'),      # La compra está parcialmente recibida
#         ('recibida', 'Recibida'),    # La compra ha sido completamente recibida
#         ('cancelada', 'Cancelada'),  # En caso de que la compra sea cancelada
#     ]

#     empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='compras')
#     proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='compras')
#     fecha = models.DateTimeField(default=timezone.now)
#     total = models.DecimalField(max_digits=14, decimal_places=2)
#     estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
#     usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='compras_creadas')

#     def calcular_total(self):
#         return sum(det.subtotal for det in self.detalles.all())

#     def save(self, *args, **kwargs):
#         # Si la instancia no tiene ID, primero guardamos para crearla
#         if not self.pk:
#             super().save(*args, **kwargs)
#         # Ahora calculamos el total basado en detalles existentes
#         total_calculado = self.calcular_total()
#         if self.total != total_calculado:
#             self.total = total_calculado
#         super().save(*args, **kwargs)  # Guardar con total actualizado

#     class Meta:
#         verbose_name = "Compra"
#         verbose_name_plural = "Compras"
#         ordering = ['-fecha']
#         indexes = [
#             models.Index(fields=['empresa', 'fecha']),
#             models.Index(fields=['estado']),
#         ]

#     def __str__(self):
#         return f'Compra #{self.id} - {self.proveedor.nombre} - {self.fecha.strftime("%Y-%m-%d")}'
class Compra(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),  # La compra está pendiente de ser recibida
        ('parcial', 'Parcial'),      # La compra está parcialmente recibida
        ('recibida', 'Recibida'),    # La compra ha sido completamente recibida
        ('cancelada', 'Cancelada'),  # En caso de que la compra sea cancelada
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='compras')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='compras')
    fecha = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=14, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='compras_creadas')

    def calcular_total(self):
        return sum(det.subtotal for det in self.detalles.all())

    def save(self, *args, **kwargs):
        if not self.pk:
            # Guardar primero para que tenga pk y pueda acceder a detalles relacionados
            super().save(*args, **kwargs)

        total_calculado = self.calcular_total()
        if self.total != total_calculado:
            self.total = total_calculado
            super().save(update_fields=['total'])
        else:
            # Si el total ya es correcto y es creación, guardamos normal para no perder datos
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['empresa', 'fecha']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f'Compra #{self.id} - {self.proveedor.nombre} - {self.fecha.strftime("%Y-%m-%d")}'

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles_compra')
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=14, decimal_places=2)
    lote = models.CharField(max_length=100, blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    cantidad_recibida = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # nuevo campo

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
    
    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a cero.")
        if self.precio_unitario <= 0:
            raise ValidationError("El precio unitario debe ser mayor a cero.")


    class Meta:
        verbose_name = "Detalle de Compra"
        verbose_name_plural = "Detalles de Compras"
        # unique_together = ('compra', 'producto')
        unique_together = ('compra', 'producto', 'lote', 'fecha_vencimiento')

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad} x {self.precio_unitario}'




# --- /home/runner/workspace/compras/tests.py ---
# compras/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from accounts.models import Usuario, Empresa
from compras.models import Compra, DetalleCompra
from inventario.models import Producto
from datetime import date

class CompraTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.empresa = Empresa.objects.create(nombre="Empresa Test")
        self.usuario = Usuario.objects.create_user(username="user1", password="pass123", empresa=self.empresa)
        self.producto1 = Producto.objects.create(nombre="Producto 1", activo=True)
        self.producto2 = Producto.objects.create(nombre="Producto 2", activo=True)

        self.client.force_authenticate(user=self.usuario)

    def test_crear_compra_con_detalles_y_total(self):
        url = reverse('compra-list')  # O el nombre correcto de tu ruta
        data = {
            "proveedor": 1,  # crea un proveedor antes o usa uno válido
            "detalles": [
                {"producto": self.producto1.id, "cantidad": 10, "precio_unitario": "5.00"},
                {"producto": self.producto2.id, "cantidad": 2, "precio_unitario": "20.00"}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['total'], '90.00')  # 10*5 + 2*20

    def test_actualizar_compra_y_recalcular_total(self):
        compra = Compra.objects.create(
            empresa=self.empresa,
            proveedor_id=1,  # igual, un proveedor válido
            usuario=self.usuario,
            total=0
        )
        DetalleCompra.objects.create(compra=compra, producto=self.producto1, cantidad=1, precio_unitario=10)
        url = reverse('compra-detail', args=[compra.id])

        data = {
            "detalles": [
                {"producto": self.producto1.id, "cantidad": 3, "precio_unitario": "15.00"}
            ],
            "estado": "pendiente"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total'], '45.00')  # 3*15

    def test_subtotal_detalle(self):
        compra = Compra.objects.create(empresa=self.empresa, proveedor_id=1, usuario=self.usuario, total=0)
        detalle = DetalleCompra.objects.create(compra=compra, producto=self.producto1, cantidad=4, precio_unitario=7.5)
        self.assertEqual(detalle.subtotal, 30.0)



# --- /home/runner/workspace/compras/migrations/__init__.py ---



# --- /home/runner/workspace/compras/migrations/0001_initial.py ---
# Generated by Django 5.2.4 on 2025-07-04 22:50

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('inventario', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('rfc', models.CharField(max_length=13)),
                ('correo', models.EmailField(blank=True, max_length=254, null=True)),
                ('telefono', models.CharField(blank=True, max_length=30, null=True)),
                ('direccion', models.TextField(blank=True, null=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proveedores', to='core.empresa')),
            ],
            options={
                'verbose_name': 'Proveedor',
                'verbose_name_plural': 'Proveedores',
                'ordering': ['nombre'],
                'unique_together': {('empresa', 'rfc')},
            },
        ),
        migrations.CreateModel(
            name='Compra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('total', models.DecimalField(decimal_places=2, max_digits=14)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('completada', 'Completada'), ('cancelada', 'Cancelada')], default='pendiente', max_length=20)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='compras', to='core.empresa')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='compras_creadas', to=settings.AUTH_USER_MODEL)),
                ('proveedor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='compras', to='compras.proveedor')),
            ],
            options={
                'verbose_name': 'Compra',
                'verbose_name_plural': 'Compras',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='DetalleCompra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=12)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=14)),
                ('compra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='compras.compra')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='detalles_compra', to='inventario.producto')),
            ],
            options={
                'verbose_name': 'Detalle de Compra',
                'verbose_name_plural': 'Detalles de Compras',
                'unique_together': {('compra', 'producto')},
            },
        ),
        migrations.AddIndex(
            model_name='compra',
            index=models.Index(fields=['empresa', 'fecha'], name='compras_com_empresa_147b8e_idx'),
        ),
        migrations.AddIndex(
            model_name='compra',
            index=models.Index(fields=['estado'], name='compras_com_estado_d26ae1_idx'),
        ),
    ]



# --- /home/runner/workspace/compras/migrations/0002_detallecompra_fecha_vencimiento_detallecompra_lote.py ---
# Generated by Django 5.2.4 on 2025-07-17 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compras', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='detallecompra',
            name='fecha_vencimiento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='detallecompra',
            name='lote',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]



# --- /home/runner/workspace/compras/migrations/0003_alter_detallecompra_unique_together.py ---
# Generated by Django 5.2.4 on 2025-07-17 23:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('compras', '0002_detallecompra_fecha_vencimiento_detallecompra_lote'),
        ('inventario', '0002_alter_inventario_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='detallecompra',
            unique_together={('compra', 'producto', 'lote', 'fecha_vencimiento')},
        ),
    ]



# --- /home/runner/workspace/compras/migrations/0004_alter_compra_estado.py ---
# Generated by Django 5.2.4 on 2025-07-17 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compras', '0003_alter_detallecompra_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compra',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('parcial', 'Parcial'), ('recibida', 'Recibida'), ('cancelada', 'Cancelada')], default='pendiente', max_length=20),
        ),
    ]



# --- /home/runner/workspace/compras/migrations/0005_detallecompra_cantidad_recibida.py ---
# Generated by Django 5.2.4 on 2025-07-18 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compras', '0004_alter_compra_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='detallecompra',
            name='cantidad_recibida',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]



# --- /home/runner/workspace/compras/views/proveedor_views.py ---
# compras/views/proveedor_views.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from compras.models import Proveedor
from compras.serializers import ProveedorSerializer
from accounts.permissions import IsSuperAdminOrCompras
from rest_framework import serializers

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    # permission_classes = [IsSuperAdminOrCompras] # 👈 Asegúrate de tener este permiso
    permission_classes = [AllowAny]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'rfc', 'correo', 'telefono']
    search_fields = ['nombre', 'rfc', 'correo']
    ordering_fields = ['nombre', 'creado_en', 'actualizado_en']
    ordering = ['nombre']

    def get_queryset(self):
        user = self.request.user
        empresa = getattr(user, 'empresa_actual', None)
        if empresa:
            return Proveedor.objects.filter(empresa=empresa)
        return Proveedor.objects.none()

    def perform_create(self, serializer):
        empresa = getattr(self.request.user, 'empresa', None)
        print("Empresa actual del usuario:", empresa)
        if empresa is None:
            # Si no hay empresa, puedes lanzar excepción o manejar el error
            raise serializers.ValidationError("No se encontró empresa asignada al usuario")
        serializer.save(empresa=empresa)



# --- /home/runner/workspace/compras/views/__init_.py ---
from .proveedor_views import ProveedorViewSet

__all__ = ['ProveedorViewSet']


# --- /home/runner/workspace/compras/views/purchase_receive_api_view.py ---
# from django.db import transaction
# from django.db.models import Q

# class PurchaseReceiveAPIView(generics.UpdateAPIView):
#     queryset = Compra.objects.all()
#     serializer_class = CompraSerializer

#     def partial_update(self, request, *args, **kwargs):
#         compra = self.get_object()

#         if compra.estado != 'pendiente':
#             return Response({'error': 'La compra ya fue recibida o cancelada.'}, status=status.HTTP_400_BAD_REQUEST)

#         detalles = compra.detalles.all()

#         with transaction.atomic():
#             for detalle in detalles.select_related('producto'):
#                 try:
#                     producto = detalle.producto
#                     sucursal = request.user.sucursal_actual
#                     lote = detalle.lote or None
#                     fecha_venc = detalle.fecha_vencimiento or None

#                     # 🔐 Bloqueamos filas para evitar condiciones de carrera
#                     inventario, _ = Inventario.objects.select_for_update().get_or_create(
#                         producto=producto,
#                         sucursal=sucursal,
#                         lote=lote,
#                         fecha_vencimiento=fecha_venc,
#                         defaults={'cantidad': 0}
#                     )

#                     # 📥 Aumentamos la cantidad en stock
#                     inventario.cantidad += detalle.cantidad
#                     inventario.save()

#                     # 📋 Registramos el movimiento de entrada
#                     MovimientoInventario.objects.create(
#                         inventario=inventario,
#                         tipo_movimiento='entrada',
#                         cantidad=detalle.cantidad,
#                         fecha=timezone.now(),
#                         usuario=request.user  # ⚠️ Verifica que tu modelo tenga `usuario`
#                     )

#                 except Exception as e:
#                     return Response({
#                         'error': f'Error al procesar producto {producto.nombre}',
#                         'detalle': str(e)
#                     }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#             # ✅ Actualizamos estado de la compra
#             compra.estado = 'recibida'
#             compra.save()

#         return Response({'mensaje': 'Compra recibida correctamente.'})



# --- /home/runner/workspace/compras/views/compra_views.py ---
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from compras.models import Compra
from compras.serializers import CompraSerializer
from accounts.permissions import IsSuperAdminOrCompras
from rest_framework import serializers
from decimal import Decimal
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from compras.models import Compra, DetalleCompra
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from inventario.models import Inventario
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from inventario.models import Inventario, MovimientoInventario
from compras.models import Compra, DetalleCompra
from datetime import datetime
from compras.filters import CompraFilter  # Importa el filtro

import django_filters  # Asegúrate de que esta línea esté presente





class CompraReceiveView(APIView):
    def patch(self, request, pk):
        compra = get_object_or_404(Compra, pk=pk)

        if compra.estado == 'recibida':
            return Response({"detail": "Esta compra ya fue recibida."}, status=status.HTTP_400_BAD_REQUEST)

        detalles = DetalleCompra.objects.filter(compra=compra).select_for_update()

        with transaction.atomic():
            for detalle in detalles:
                cantidad_pendiente = detalle.cantidad - detalle.cantidad_recibida
                if cantidad_pendiente <= 0:
                    continue  # Ya recibido, no sumar más

                inventario, _ = Inventario.objects.select_for_update().get_or_create(
                    producto=detalle.producto,
                    sucursal=compra.usuario.sucursal_actual,
                    lote=detalle.lote or None,
                    fecha_vencimiento=detalle.fecha_vencimiento or None,
                    defaults={"cantidad": 0}
                )
                inventario.cantidad += cantidad_pendiente
                inventario.save()

                MovimientoInventario.objects.create(
                    inventario=inventario,
                    tipo_movimiento='entrada',
                    cantidad=cantidad_pendiente,
                    fecha=datetime.now(),
                    usuario=compra.usuario
                )

                detalle.cantidad_recibida = detalle.cantidad
                detalle.save()

            # Actualiza estado
            if all(d.cantidad_recibida >= d.cantidad for d in compra.detalles.all()):
                compra.estado = 'recibida'
            elif any(d.cantidad_recibida > 0 for d in compra.detalles.all()):
                compra.estado = 'parcial'
            else:
                compra.estado = 'pendiente'
            compra.save()

        return Response({"detail": "Compra recibida correctamente."}, status=status.HTTP_200_OK)


class ReceivePurchase(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        # Buscar la compra por ID
        compra = get_object_or_404(Compra, id=id)

        # Validar si el estado es "pendiente" o "parcial", no debería estar ya "recibida"
        if compra.estado not in ['pendiente', 'parcial']:
            raise ValidationError("La compra ya ha sido recibida o está cancelada.")

        # Actualizar el estado a 'recibida' (si ya es parcial o pendiente)
        compra.estado = 'recibida'
        compra.save()

        # Verificar que el usuario tiene sucursal asignada
        sucursal = request.user.sucursal_actual
        if not sucursal:
            raise ValidationError("El usuario no tiene una sucursal asignada.")

        # Actualizar el stock de los productos en inventario
        for detalle in compra.detalles.all():
            producto = detalle.producto
            cantidad = detalle.cantidad

            # Obtener el inventario para esa sucursal, lote y producto
            inventario, creado = Inventario.objects.get_or_create(
                producto=producto,
                sucursal=sucursal,  # Sucursal obtenida del usuario
                lote=detalle.lote,
                fecha_vencimiento=detalle.fecha_vencimiento,
                defaults={'cantidad': 0}
            )

            # Incrementar la cantidad en el inventario
            inventario.cantidad += cantidad
            inventario.save()

        return Response({"message": "Compra recibida y stock actualizado."}, status=status.HTTP_200_OK)

# Personaliza la respuesta de los errores de validación
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # Personaliza el formato de la respuesta de error
        if isinstance(exc, ValidationError):
            response.data = {"detail": response.data[0]}  # Cambia el arreglo por un mensaje directo

    return response


# class CompraFilter(django_filters.FilterSet):
#     fecha_compra = django_filters.DateFilter(field_name='fecha', lookup_expr='exact')
#     fecha_min = django_filters.DateFilter(field_name='fecha', lookup_expr='gte')
#     fecha_max = django_filters.DateFilter(field_name='fecha', lookup_expr='lte')
#     total_min = django_filters.NumberFilter(field_name='total', lookup_expr='gte')
#     total_max = django_filters.NumberFilter(field_name='total', lookup_expr='lte')
#     nombre_producto = django_filters.CharFilter(method='filter_nombre_producto')
#     producto_id = django_filters.NumberFilter(field_name='detalles__producto__id')
#     producto_id__in = django_filters.BaseInFilter(field_name='detalles__producto__id', lookup_expr='in')

#     class Meta:
#         model = Compra
#         fields = ['empresa', 'proveedor', 'estado', 'fecha_compra']

#     def filter_nombre_producto(self, queryset, name, value):
#         return queryset.filter(detalles__producto__nombre__icontains=value).distinct()

# class CompraFilter(django_filters.FilterSet):
#     fecha_compra = django_filters.DateFilter(field_name='fecha', lookup_expr='exact')
#     nombre_producto = django_filters.CharFilter(method='filter_nombre_producto')

#     class Meta:
#         model = Compra
#         fields = ['empresa', 'proveedor', 'fecha_compra']

#     def filter_nombre_producto(self, queryset, name, value):
#         # Aquí usamos Q para hacer una búsqueda en la relación detalles -> producto -> nombre
#         return queryset.filter(
#             Q(detalles__producto__nombre__icontains=value)
#         ).distinct()  # Evita duplicados de compras que contienen varios productos coincidentes


# from rest_framework import viewsets, filters
# from django_filters.rest_framework import DjangoFilterBackend
# from .models import Compra
# from .serializers import CompraSerializer
# from .filters import CompraFilter


# /api/purchases/purchases/?search=camiseta
# /api/purchases/purchases/?proveedor=3
# /api/purchases/purchases/?fecha_min=2025-07-01&fecha_max=2025-07-31
# /api/purchases/purchases/?total_min=100&total_max=1000
# /api/purchases/purchases/?producto_id=7
# /api/purchases/purchases/?producto_id__in=5,7,8
# /api/purchases/purchases/?ordering=total
# /api/purchases/purchases/?ordering=-fecha


class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer

    filter_backends = [
        DjangoFilterBackend,       # Para filtros personalizados
        filters.SearchFilter,      # Para búsqueda general
        filters.OrderingFilter     # Para ordenamiento
    ]

    filterset_class = CompraFilter

    # Búsqueda tipo Google
    search_fields = [
        'detalles__producto__nombre',
        'detalles__producto__codigo',
        'proveedor__nombre',
        'detalles__lote'
    ]

    # Campos que se pueden ordenar
    ordering_fields = ['fecha', 'total']
    ordering = ['-fecha']  # Por defecto, mostrar compras recientes primero

    def get_queryset(self):
        usuario = self.request.user
        empresa = getattr(usuario, 'empresa', None)
        if empresa:
            return Compra.objects.filter(empresa=empresa)
        return Compra.objects.none()

    def perform_create(self, serializer):
        usuario = self.request.user
        empresa = usuario.empresa
        if not getattr(usuario, 'sucursal_actual', None):
            raise serializers.ValidationError("El usuario no tiene una sucursal asignada.")
        serializer.save(empresa=empresa, usuario=usuario)



class CompraRecepcionParcialAPIView(APIView):
    def patch(self, request, pk):
        try:
            compra = Compra.objects.select_for_update().get(pk=pk)
        except Compra.DoesNotExist:
            return Response({'detail': 'Compra no encontrada.'}, status=404)

        data = request.data.get("items", [])
        if not data:
            return Response({'detail': 'No se enviaron productos a recibir.'}, status=400)

        resultados = []
        cambios_realizados = False

        with transaction.atomic():
            for item in data:
                detalle_id = item.get('detalle_id')
                recibido = item.get('recibido')

                if not detalle_id or recibido is None:
                    resultados.append({
                        'detalle_id': detalle_id,
                        'status': 'error',
                        'message': 'Faltan datos de detalle o cantidad recibida.'
                    })
                    continue

                try:
                    recibido = Decimal(recibido)
                except:
                    resultados.append({
                        'detalle_id': detalle_id,
                        'status': 'error',
                        'message': 'Cantidad recibida inválida.'
                    })
                    continue

                if recibido <= 0:
                    resultados.append({
                        'detalle_id': detalle_id,
                        'status': 'error',
                        'message': 'Cantidad recibida debe ser mayor a cero.'
                    })
                    continue

                try:
                    detalle = DetalleCompra.objects.select_for_update().get(id=detalle_id, compra=compra)
                except DetalleCompra.DoesNotExist:
                    resultados.append({
                        'detalle_id': detalle_id,
                        'status': 'error',
                        'message': 'Detalle no encontrado.'
                    })
                    continue

                cantidad_pendiente = detalle.cantidad - detalle.cantidad_recibida

                if cantidad_pendiente <= 0:
                    resultados.append({
                        'detalle_id': detalle_id,
                        'status': 'sin_cambios',
                        'message': 'Ya se recibió la cantidad completa para este detalle.'
                    })
                    continue

                recibido_real = min(recibido, cantidad_pendiente)

                # Actualiza cantidad recibida solo con lo que falta
                detalle.cantidad_recibida += recibido_real
                detalle.save()

                lote = detalle.lote or None
                vencimiento = detalle.fecha_vencimiento or None

                inventario, _ = Inventario.objects.select_for_update().get_or_create(
                    producto=detalle.producto,
                    sucursal=compra.usuario.sucursal_actual,
                    lote=lote,
                    fecha_vencimiento=vencimiento,
                    defaults={'cantidad': 0}
                )
                inventario.cantidad += recibido_real
                inventario.save()

                MovimientoInventario.objects.create(
                    inventario=inventario,
                    tipo_movimiento='entrada',
                    cantidad=recibido_real,
                    fecha=timezone.now(),
                    usuario=request.user
                )

                cambios_realizados = True

                resultados.append({
                    'detalle_id': detalle_id,
                    'status': 'recibido',
                    'cantidad_recibida': str(recibido_real),
                    'message': 'Cantidad recibida y stock actualizado.'
                })

            # Luego actualiza estado según cantidades recibidas
            if all(d.cantidad_recibida >= d.cantidad for d in compra.detalles.all()):
                compra.estado = 'recibida'
            elif any(d.cantidad_recibida > 0 for d in compra.detalles.all()):
                compra.estado = 'parcial'
            else:
                compra.estado = 'pendiente'
            compra.save()

        if cambios_realizados:
            return Response({
                'detail': 'Recepción procesada correctamente.',
                'resultados': resultados
            })
        else:
            return Response({
                'detail': 'No se realizaron cambios. Posiblemente todo ya estaba recibido.',
                'resultados': resultados
            }, status=400)


class CompraCancelarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        compra = get_object_or_404(Compra, pk=pk)

        # Si la compra ya está cancelada, no se debe hacer nada
        if compra.estado == 'cancelada':
            return Response({"detail": "La compra ya está cancelada."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si la compra ya fue recibida (parcial o completa)
        if compra.estado == 'recibida' or compra.estado == 'parcial':
            with transaction.atomic():
                for detalle in compra.detalles.all():
                    if detalle.cantidad_recibida > 0:
                        # Ajustar inventario y registrar movimiento de salida (devolución)
                        inventario = Inventario.objects.filter(
                            producto=detalle.producto,
                            sucursal=compra.usuario.sucursal_actual,
                            lote=detalle.lote,
                            fecha_vencimiento=detalle.fecha_vencimiento
                        ).first()

                        if inventario:
                            # Restar del inventario lo recibido
                            inventario.cantidad -= detalle.cantidad_recibida
                            inventario.save()

                            # Registrar el movimiento como salida (devolución)
                            MovimientoInventario.objects.create(
                                inventario=inventario,
                                tipo_movimiento='salida',  # Salida porque es una devolución
                                cantidad=detalle.cantidad_recibida,
                                fecha=timezone.now(),
                                usuario=request.user
                            )

                        # Resetear cantidad recibida a 0
                        detalle.cantidad_recibida = 0
                        detalle.save()

            compra.estado = 'cancelada'
            compra.save()
            return Response({"detail": "Compra cancelada y stock ajustado correctamente."}, status=status.HTTP_200_OK)

        # Si la compra no ha sido recibida aún, solo se cambia el estado a 'cancelada'
        compra.estado = 'cancelada'
        compra.save()

        return Response({"detail": "Compra cancelada correctamente, no se ajustó el inventario."}, status=status.HTTP_200_OK)
            



# --- /home/runner/workspace/compras/serializers/proveedor_serializers.py ---
# compras/serializers.py
from rest_framework import serializers
from compras.models import Proveedor, Compra, DetalleCompra
# from compras.models import Proveedor, Compra, DetalleCompra

from inventario.models import Producto

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = [
            'id', 'empresa', 'nombre', 'rfc', 'correo', 'telefono', 'direccion',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']


# --- /home/runner/workspace/compras/serializers/__init__.py ---
from .proveedor_serializers import ProveedorSerializer
from .detalle_compra_serializers import DetalleCompraSerializer
from .compra_serializers import CompraSerializer

__all__ = [
    'ProveedorSerializer',
    'DetalleCompraSerializer',
    'CompraSerializer',
]
# from .proveedor_serializers import ProveedorSerializer
# from .detalle_compra_serializers import DetalleCompraSerializer
# from .compra_serializers import CompraSerializer

# __all__ = [
#     'ProveedorSerializer',
#     'DetalleCompraSerializer',
#     'CompraSerializer',
# ]


# --- /home/runner/workspace/compras/serializers/detalle_compra_serializers.py ---
# compras/serializers.py
from rest_framework import serializers
# from .models import  DetalleCompra
from compras.models import DetalleCompra
# from compras.serializers.detalle_compra_serializers import DetalleCompraSerializer

from inventario.models import Producto


class DetalleCompraSerializer(serializers.ModelSerializer):
    nombre_producto = serializers.CharField(source='producto.nombre', read_only=True)
    lote = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fecha_vencimiento = serializers.DateField(required=False, allow_null=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = DetalleCompra
        fields = [
            'id', 'producto', 'nombre_producto', 'cantidad', 'precio_unitario',
            'lote', 'fecha_vencimiento', 'subtotal'
        ]

    def get_subtotal(self, obj):
        return obj.subtotal
    

    def validate(self, data):
        producto = data.get('producto')
        cantidad = data.get('cantidad')
        precio_unitario = data.get('precio_unitario')

        if producto and not producto.activo:
            raise serializers.ValidationError("El producto seleccionado está inactivo.")

        if cantidad is not None and cantidad <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a cero.")

        if precio_unitario is not None and precio_unitario <= 0:
            raise serializers.ValidationError("El precio unitario debe ser mayor a cero.")

        return data


# --- /home/runner/workspace/compras/serializers/compra_serializers.py ---
from rest_framework import serializers
from compras.models import Proveedor, Compra, DetalleCompra
from compras.serializers.detalle_compra_serializers import DetalleCompraSerializer
from inventario.models import Inventario, MovimientoInventario
from django.db import transaction
from finanzas.models import CuentaPorPagar
from datetime import timedelta

class CompraSerializer(serializers.ModelSerializer):
    detalles = DetalleCompraSerializer(many=True)
    total = serializers.SerializerMethodField()
    nombre_proveedor = serializers.CharField(source='proveedor.nombre', read_only=True)

    class Meta:
        model = Compra
        fields = [
            'id', 'empresa', 'proveedor', 'nombre_proveedor', 'fecha', 'estado',
            'usuario', 'total', 'detalles'
        ]
        read_only_fields = ['id', 'total', 'usuario', 'empresa']

    def get_total(self, obj):
        return sum(det.cantidad * det.precio_unitario for det in obj.detalles.all())

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')

        request = self.context.get('request')
        usuario = request.user if request else None
        sucursal = getattr(usuario, 'sucursal_actual', None)
        empresa = getattr(usuario, 'empresa', None)

        if not usuario or not usuario.is_authenticated:
            raise serializers.ValidationError("Usuario no autenticado.")
        if not sucursal:
            raise serializers.ValidationError("El usuario no tiene una sucursal asignada.")
        if not empresa:
            raise serializers.ValidationError("El usuario no tiene empresa asignada.")

        total = sum(d['cantidad'] * d['precio_unitario'] for d in detalles_data)

        validated_data['empresa'] = empresa
        validated_data['usuario'] = usuario
        validated_data['total'] = total

        with transaction.atomic():
            compra = Compra.objects.create(**validated_data)
            for detalle_data in detalles_data:
                DetalleCompra.objects.create(compra=compra, **detalle_data)

            # Crear CuentaPorPagar automáticamente
            fecha_vencimiento = compra.fecha + timedelta(days=30)  # Ejemplo plazo 30 días
            CuentaPorPagar.objects.create(
                empresa=empresa,
                compra=compra,
                monto=total,
                fecha_vencimiento=fecha_vencimiento,
                estado='PENDIENTE'
            )

        return compra

# class CompraSerializer(serializers.ModelSerializer):
#     detalles = DetalleCompraSerializer(many=True)
#     # total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
#     total = serializers.SerializerMethodField()  # <- Cambiado
#     nombre_proveedor = serializers.CharField(source='proveedor.nombre', read_only=True)

#     class Meta:
#         model = Compra
#         fields = [
#             'id', 'empresa', 'proveedor', 'nombre_proveedor', 'fecha', 'estado',
#             'usuario', 'total', 'detalles'
#         ]
#         read_only_fields = ['id', 'total', 'usuario', 'empresa']


#     def get_total(self, obj):
#         return sum(det.cantidad * det.precio_unitario for det in obj.detalles.all())


#     def validate(self, data):
#       detalles = data.get('detalles', [])
#       productos = {}
  
#       for detalle in detalles:
#           producto = detalle['producto']
#           lote = detalle.get('lote', '')
#           fecha_vencimiento = detalle.get('fecha_vencimiento', None)
  
#           # Usa un identificador único por producto, lote y fecha_vencimiento
#           clave_producto = (producto.id, lote, fecha_vencimiento)
  
#           if clave_producto in productos:
#               raise serializers.ValidationError(
#                   f"Producto duplicado: '{producto.nombre}' ya está incluido en los detalles con el mismo lote y fecha de vencimiento."
#               )
  
#           productos[clave_producto] = detalle
  
#       return data

#     def calcular_total_detalles(self, detalles_data):
#         return sum(
#             detalle['cantidad'] * detalle['precio_unitario']
#             for detalle in detalles_data
#         )

#     def create(self, validated_data):
#         request = self.context.get('request')
#         usuario = request.user if request else None
#         sucursal = getattr(usuario, 'sucursal_actual', None)
#         empresa = getattr(usuario, 'empresa', None)

#         if not usuario or not usuario.is_authenticated:
#             raise serializers.ValidationError("Usuario no autenticado.")
#         if not sucursal:
#             raise serializers.ValidationError("El usuario no tiene una sucursal asignada.")
#         if not empresa:
#             raise serializers.ValidationError("El usuario no tiene empresa asignada.")

#         detalles_data = validated_data.pop('detalles')

#         total = self.calcular_total_detalles(detalles_data)
#         validated_data['empresa'] = empresa
#         validated_data['usuario'] = usuario
#         validated_data['total'] = total

#         with transaction.atomic():
#             compra = Compra.objects.create(**validated_data)

#             for detalle_data in detalles_data:
#                 DetalleCompra.objects.create(compra=compra, **detalle_data)

#         return compra


#     def update(self, instance, validated_data):
#         detalles_data = validated_data.pop('detalles', None)

#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)

#         if detalles_data is not None:
#             instance.detalles.all().delete()
#             total = 0
#             for detalle_data in detalles_data:
#                 DetalleCompra.objects.create(compra=instance, **detalle_data)
#                 total += detalle_data['cantidad'] * detalle_data['precio_unitario']
#             instance.total = total

#         instance.save()
#         return instance


