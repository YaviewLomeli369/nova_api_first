
# --- /home/runner/workspace/ventas/__init__.py ---



# --- /home/runner/workspace/ventas/admin.py ---
from django.contrib import admin

# Register your models here.



# --- /home/runner/workspace/ventas/apps.py ---
from django.apps import AppConfig


class VentasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ventas'



# --- /home/runner/workspace/ventas/tests.py ---
from django.test import TestCase

# Create your tests here.



# --- /home/runner/workspace/ventas/signals.py ---
# ventas/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, F
from .models import DetalleVenta, Venta

def actualizar_total_venta(venta_id):
    try:
        venta = Venta.objects.get(id=venta_id)
    except Venta.DoesNotExist:
        return  # Si no existe, nada que hacer

    total = venta.detalles.aggregate(
        total=Sum(F('cantidad') * F('precio_unitario'))
    )['total'] or 0

    # Actualizar solo si cambió para evitar saves innecesarios
    if venta.total != total:
        venta.total = total
        venta.save(update_fields=['total'])

@receiver(post_save, sender=DetalleVenta)
def detalleventa_guardado(sender, instance, **kwargs):
    actualizar_total_venta(instance.venta_id)

@receiver(post_delete, sender=DetalleVenta)
def detalleventa_eliminado(sender, instance, **kwargs):
    actualizar_total_venta(instance.venta_id)



# --- /home/runner/workspace/ventas/app.py ---
# ventas/apps.py

from django.apps import AppConfig

class VentasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ventas'

    def ready(self):
        import ventas.signals



# --- /home/runner/workspace/ventas/utils.py ---
import xml.etree.ElementTree as ET
from django.core.files.base import ContentFile
from django.utils import timezone

def generar_xml_desde_comprobante(comprobante):
    """
    Genera un XML básico desde un objeto comprobante.
    Ajusta esto según el estándar fiscal (ej. CFDI, UBL, etc.).
    """
    # Estructura básica del XML
    root = ET.Element("Comprobante")
    ET.SubElement(root, "UUID").text = comprobante.uuid if hasattr(comprobante, 'uuid') else "UUID-Generico"
    ET.SubElement(root, "Fecha").text = timezone.now().isoformat()
    ET.SubElement(root, "Total").text = str(comprobante.total)

    # Agrega otros campos relevantes aquí
    # ...

    # Convierte el árbol a una cadena de bytes
    xml_string = ET.tostring(root, encoding="utf-8", method="xml")

    # Opcional: Guarda el XML en el modelo (si tiene campo FileField)
    if hasattr(comprobante, 'archivo_xml'):
        comprobante.archivo_xml.save(f"{comprobante.id}.xml", ContentFile(xml_string), save=True)

    return xml_string


# --- /home/runner/workspace/ventas/urls.py ---
# ventas/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path
from ventas.views import ClienteViewSet, VentaViewSet, DetalleVentaViewSet
from ventas.views.dashboard import VentaDashboardAPIView  # Asegúrate de importar desde el archivo correcto
# from ventas.views.facturar_venta import FacturarVentaAPIView  # Asegúrate que esta vista existe y está bien importada
# Instanciamos el router
router = DefaultRouter()
router.register(r'costumers', ClienteViewSet)
router.register(r'orders', VentaViewSet)
router.register(r'details', DetalleVentaViewSet)

# Añadimos el endpoint del dashboard de ventas fuera del router
urlpatterns = router.urls + [
    path('dashboard/', VentaDashboardAPIView.as_view(), name='venta-dashboard'),
    # path('invoice-sale/<int:id>/', FacturarVentaAPIView.as_view(), name='facturar-venta'),
]




# --- /home/runner/workspace/ventas/models.py ---
# ventas/models.py (completado)

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Cliente(models.Model):
    empresa = models.ForeignKey('core.Empresa', on_delete=models.CASCADE, related_name='clientes')
    nombre = models.CharField(max_length=200)
    apellido_paterno = models.CharField(max_length=100, blank=True, null=True)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    rfc = models.CharField(max_length=13, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    uso_cfdi = models.CharField(max_length=3, blank=True, null=True, help_text="Uso CFDI SAT (G03, S01, etc.)")
    regimen_fiscal = models.CharField(max_length=3, blank=True, null=True, help_text="Régimen fiscal del receptor")

    direccion_calle = models.CharField(max_length=150, blank=True, null=True)
    direccion_num_ext = models.CharField(max_length=10, blank=True, null=True)
    direccion_num_int = models.CharField(max_length=10, blank=True, null=True)
    direccion_colonia = models.CharField(max_length=100, blank=True, null=True)
    direccion_municipio = models.CharField(max_length=100, blank=True, null=True)
    direccion_estado = models.CharField(max_length=100, blank=True, null=True)
    direccion_pais = models.CharField(max_length=50, default='MEX')
    direccion_codigo_postal = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['empresa', 'nombre']),
        ]

    @property
    def nombre_completo(self):
        apellidos = ' '.join(filter(None, [self.apellido_paterno, self.apellido_materno]))
        return f"{self.nombre} {apellidos}".strip()

    def clean(self):
        if self.rfc and self.uso_cfdi == "P01" and self.rfc != "XAXX010101000":
            raise ValidationError("El uso CFDI 'P01' solo es válido con RFC genérico.")

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]

    empresa = models.ForeignKey('core.Empresa', on_delete=models.CASCADE, related_name='ventas')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas')
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=14, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')
    usuario = models.ForeignKey('accounts.Usuario', on_delete=models.PROTECT, related_name='ventas')
    condiciones_pago = models.CharField(max_length=100, blank=True, null=True, help_text="Ej: Contado, Crédito 30 días")
    moneda = models.CharField(max_length=5, blank=True, null=True, default="MXN", help_text="Ej: MXN, USD")

    FORMA_PAGO_CHOICES = [
        ('01', 'Efectivo'),
        ('02', 'Cheque nominativo'),
        ('03', 'Transferencia electrónica de fondos'),
        ('04', 'Tarjeta de crédito'),
        ('05', 'Monedero electrónico'),
        ('06', 'Dinero electrónico'),
        ('08', 'Vales de despensa'),
        ('12', 'Dación en pago'),
        ('13', 'Pago por subrogación'),
        ('14', 'Pago por consignación'),
        ('15', 'Condonación'),
        ('17', 'Compensación'),
        ('23', 'Novación'),
        ('24', 'Confusión'),
        ('25', 'Remisión de deuda'),
        ('26', 'Prescripción o caducidad'),
        ('27', 'A satisfacción del acreedor'),
        ('28', 'Tarjeta de débito'),
        ('29', 'Tarjeta de servicios'),
        ('30', 'Aplicación de anticipos'),
        ('31', 'Intermediario pagos'),
        ('99', 'Por definir'),
    ]

    METODO_PAGO_CHOICES = [
        ('PUE', 'Pago en una sola exhibición'),
        ('PPD', 'Pago en parcialidades o diferido'),
    ]

    forma_pago = models.CharField(
        max_length=2,
        choices=FORMA_PAGO_CHOICES,
        default='01'
    )

    metodo_pago = models.CharField(
        max_length=3,
        choices=METODO_PAGO_CHOICES,
        default='PUE'
    )

    def calcular_total(self):
        # Solo calcular si ya tenemos un ID (la venta ya fue guardada)
        if self.pk:
            self.total = sum(detalle.precio_unitario * detalle.cantidad for detalle in self.detalles.all())
        else:
            # Si no tiene ID, establecer total en 0 inicialmente
            self.total = 0

    def save(self, *args, **kwargs):
        if not self.pk:
            self.total = 0
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['empresa', 'fecha']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f"Venta {self.id} - {self.cliente.nombre} - {self.estado}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('inventario.Producto', on_delete=models.PROTECT, related_name='ventas_detalle')
    cantidad = models.DecimalField(max_digits=14, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=14, decimal_places=2)

    @property
    def importe(self):
        return Decimal(self.precio_unitario) * Decimal(self.cantidad)


    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a cero.")
        if self.precio_unitario <= 0:
            raise ValidationError("El precio unitario debe ser mayor a cero.")

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"
        indexes = [
            models.Index(fields=['producto']),
        ]

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} @ {self.precio_unitario}"

@receiver([post_save, post_delete], sender=DetalleVenta)
def actualizar_total_venta(sender, instance, **kwargs):
    venta = instance.venta
    total = venta.detalles.aggregate(
        total=models.Sum(models.F('precio_unitario') * models.F('cantidad'))
    )['total'] or 0
    venta.total = total
    venta.save(update_fields=['total'])


# --- /home/runner/workspace/ventas/migrations/__init__.py ---



# --- /home/runner/workspace/ventas/migrations/0001_initial.py ---
# Generated by Django 5.2.4 on 2025-07-30 21:47

import django.db.models.deletion
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
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('apellido_paterno', models.CharField(blank=True, max_length=100, null=True)),
                ('apellido_materno', models.CharField(blank=True, max_length=100, null=True)),
                ('rfc', models.CharField(blank=True, max_length=13, null=True)),
                ('correo', models.EmailField(blank=True, max_length=254, null=True)),
                ('telefono', models.CharField(blank=True, max_length=20, null=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('uso_cfdi', models.CharField(blank=True, help_text='Uso CFDI SAT (G03, S01, etc.)', max_length=3, null=True)),
                ('regimen_fiscal', models.CharField(blank=True, help_text='Régimen fiscal del receptor', max_length=3, null=True)),
                ('direccion_calle', models.CharField(blank=True, max_length=150, null=True)),
                ('direccion_num_ext', models.CharField(blank=True, max_length=10, null=True)),
                ('direccion_num_int', models.CharField(blank=True, max_length=10, null=True)),
                ('direccion_colonia', models.CharField(blank=True, max_length=100, null=True)),
                ('direccion_municipio', models.CharField(blank=True, max_length=100, null=True)),
                ('direccion_estado', models.CharField(blank=True, max_length=100, null=True)),
                ('direccion_pais', models.CharField(default='MEX', max_length=50)),
                ('direccion_codigo_postal', models.CharField(blank=True, max_length=10, null=True)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clientes', to='core.empresa')),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=14)),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('COMPLETADA', 'Completada'), ('CANCELADA', 'Cancelada')], default='PENDIENTE', max_length=10)),
                ('condiciones_pago', models.CharField(blank=True, help_text='Ej: Contado, Crédito 30 días', max_length=100, null=True)),
                ('moneda', models.CharField(blank=True, default='MXN', help_text='Ej: MXN, USD', max_length=5, null=True)),
                ('forma_pago', models.CharField(choices=[('01', 'Efectivo'), ('02', 'Cheque nominativo'), ('03', 'Transferencia electrónica de fondos'), ('04', 'Tarjeta de crédito'), ('05', 'Monedero electrónico'), ('06', 'Dinero electrónico'), ('08', 'Vales de despensa'), ('12', 'Dación en pago'), ('13', 'Pago por subrogación'), ('14', 'Pago por consignación'), ('15', 'Condonación'), ('17', 'Compensación'), ('23', 'Novación'), ('24', 'Confusión'), ('25', 'Remisión de deuda'), ('26', 'Prescripción o caducidad'), ('27', 'A satisfacción del acreedor'), ('28', 'Tarjeta de débito'), ('29', 'Tarjeta de servicios'), ('30', 'Aplicación de anticipos'), ('31', 'Intermediario pagos'), ('99', 'Por definir')], default='01', max_length=2)),
                ('metodo_pago', models.CharField(choices=[('PUE', 'Pago en una sola exhibición'), ('PPD', 'Pago en parcialidades o diferido')], default='PUE', max_length=3)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ventas', to='ventas.cliente')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ventas', to='core.empresa')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ventas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Venta',
                'verbose_name_plural': 'Ventas',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='DetalleVenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=14)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=14)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ventas_detalle', to='inventario.producto')),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='ventas.venta')),
            ],
            options={
                'verbose_name': 'Detalle de Venta',
                'verbose_name_plural': 'Detalles de Venta',
            },
        ),
        migrations.AddIndex(
            model_name='cliente',
            index=models.Index(fields=['empresa', 'nombre'], name='ventas_clie_empresa_dbb1c0_idx'),
        ),
        migrations.AddIndex(
            model_name='venta',
            index=models.Index(fields=['empresa', 'fecha'], name='ventas_vent_empresa_f0b283_idx'),
        ),
        migrations.AddIndex(
            model_name='venta',
            index=models.Index(fields=['estado'], name='ventas_vent_estado_b0d674_idx'),
        ),
        migrations.AddIndex(
            model_name='detalleventa',
            index=models.Index(fields=['producto'], name='ventas_deta_product_0f454d_idx'),
        ),
    ]



# --- /home/runner/workspace/ventas/filters/clientes.py ---
# ventas/filters/clientes.py
import django_filters
from ventas.models import Cliente

class ClienteFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    rfc = django_filters.CharFilter(lookup_expr='icontains')
    correo = django_filters.CharFilter(lookup_expr='icontains')
    telefono = django_filters.CharFilter(lookup_expr='icontains')
    creado_en = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Cliente
        fields = ['empresa', 'nombre', 'rfc', 'correo', 'telefono', 'creado_en']



# --- /home/runner/workspace/ventas/serializers/cliente_serializer.py ---
from rest_framework import serializers
from ventas.models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            'id',
            'empresa',
            'nombre',
            'rfc',
            'correo',
            'telefono',
            'direccion',
            'creado_en',
            'actualizado_en',
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']



# --- /home/runner/workspace/ventas/serializers/__init__.py ---
from .cliente_serializer import ClienteSerializer
from .detalle_venta_serializer import DetalleVentaSerializer
from .venta_serializer import VentaSerializer


# --- /home/runner/workspace/ventas/serializers/detalle_venta_serializer.py ---
from rest_framework import serializers
from ventas.models import DetalleVenta
from inventario.models import Inventario

class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = DetalleVenta
        fields = [
            'id',
            'producto',
            'producto_nombre',
            'cantidad',
            'precio_unitario',
            'subtotal',
        ]

    def get_subtotal(self, obj):
        return obj.cantidad * obj.precio_unitario

    def validate(self, data):
        cantidad = data.get('cantidad')
        precio_unitario = data.get('precio_unitario')
        producto = data.get('producto')

        if cantidad is None or cantidad <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a cero.")
        if precio_unitario is None or precio_unitario <= 0:
            raise serializers.ValidationError("El precio unitario debe ser mayor a cero.")
        if producto is None:
            raise serializers.ValidationError("El producto es obligatorio.")

        # Obtener todos los inventarios asociados al producto
        inventarios = Inventario.objects.filter(producto=producto)

        # Sumar la cantidad disponible de los inventarios
        stock_disponible = sum(inventario.cantidad for inventario in inventarios)

        # Verificar si hay suficiente stock
        if stock_disponible < cantidad:
            raise serializers.ValidationError(
                f"No hay suficiente stock para el producto '{producto.nombre}'. Stock disponible: {stock_disponible}"
            )

        return data



# --- /home/runner/workspace/ventas/serializers/venta_serializer.py ---
from rest_framework import serializers
from ventas.models import Venta, DetalleVenta
from .detalle_venta_serializer import DetalleVentaSerializer
from inventario.models import Producto, Inventario
from contabilidad.helpers.asientos import generar_asiento_para_venta
from django.db import transaction
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import F
from django.conf import settings
import base64
from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework.exceptions import ValidationError as DRFValidationError
from facturacion.models import MetodoPagoChoices, FormaPagoChoices, ComprobanteFiscal
from facturacion.services.facturama import FacturamaService
from facturacion.utils.build_facturama_payload import build_facturama_payload
# from facturacion.utils.build_facturama_payload import MetodoPagoChoices
from finanzas.models import CuentaPorCobrar
from django.db.models import TextChoices

from facturacion.services.timbrado_helpers import intentar_timbrado_comprobante

def redondear_decimal(valor, decimales=2):
    if not isinstance(valor, Decimal):
        valor = Decimal(str(valor))
    return valor.quantize(Decimal('1.' + '0' * decimales), rounding=ROUND_HALF_UP)

class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Venta
        fields = [
            'id',
            'empresa',
            'cliente',
            'cliente_nombre',
            'usuario',
            'usuario_username',
            'fecha',
            'total',
            'estado',
            'forma_pago',
            'metodo_pago',
            'condiciones_pago',
            'detalles'
        ]
        read_only_fields = ['id', 'fecha', 'total']

    @transaction.atomic
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')

        request = self.context.get('request')
        usuario = request.user if request else None
        empresa = getattr(usuario, 'empresa', None)

        if usuario is None:
            raise DRFValidationError("Usuario no autenticado.")
        if empresa is None:
            raise DRFValidationError("El usuario no tiene una empresa asignada.")

        # 1. Crear la venta
        venta = Venta(**validated_data)
        venta.usuario = usuario
        venta.empresa = empresa
        venta.save()

        # 2. Crear detalles y actualizar inventario
        total_calculado = Decimal('0.00')
        detalles = []

        for detalle_data in detalles_data:
            producto = detalle_data['producto']
            cantidad = detalle_data.get('cantidad')
            precio_unitario = detalle_data.get('precio_unitario')

            inventario = Inventario.objects.select_for_update().filter(
                producto=producto,
                sucursal__empresa=empresa
            ).first()

            if not inventario:
                raise DRFValidationError(f"No hay inventario para el producto {producto.nombre}")

            if inventario.cantidad < cantidad:
                raise DRFValidationError(f"Stock insuficiente para producto {producto.nombre}")

            inventario.cantidad = F('cantidad') - cantidad
            inventario.save()
            inventario.refresh_from_db()

            detalle = DetalleVenta(venta=venta, **detalle_data)
            detalles.append(detalle)

            total_calculado += cantidad * precio_unitario

        DetalleVenta.objects.bulk_create(detalles)

        venta.total = redondear_decimal(total_calculado)
        venta.save(update_fields=['total'])

        

        # 3. Crear ComprobanteFiscal en PENDIENTE
        def generar_folio(empresa):
            ultimo = ComprobanteFiscal.objects.filter(empresa=empresa, serie='A').order_by('-folio').first()
            return (ultimo.folio + 1) if ultimo and ultimo.folio else 1
            
        serie = 'A'
        folio = generar_folio(empresa)


        # Guardar primero para asegurar que comprobante.id esté disponible
        comprobante = ComprobanteFiscal.objects.create(
            empresa=empresa,
            venta=venta,
            estado='PENDIENTE',
            tipo='FACTURA',
            serie=serie,
            folio=folio
        )

        # Forzar guardado si estás inseguro de que tenga ID
        if not comprobante.id:
            comprobante.save()




        try:
            # intentar_timbrado_comprobante(comprobante)
            intentar_timbrado_comprobante(comprobante, request=request)
        except Exception as e:
            raise DRFValidationError(f"Error al timbrar comprobante: {str(e)}")

        # 5. Crear CuentaPorCobrar
        fecha_vencimiento = venta.fecha + timedelta(days=30)
        CuentaPorCobrar.objects.create(
            empresa=empresa,
            venta=venta,
            monto=venta.total,
            fecha_vencimiento=fecha_vencimiento,
            estado='PENDIENTE'
        )

        # 6. Generar asiento contable
        try:
            generar_asiento_para_venta(venta, usuario)
        except Exception as e:
            raise DRFValidationError(f"Error al generar asiento contable: {str(e)}")



        return venta


# --- /home/runner/workspace/ventas/views/__init__.py ---
from .clientes import ClienteViewSet
from .ventas import VentaViewSet
from .detallesventa import DetalleVentaViewSet


# --- /home/runner/workspace/ventas/views/detallesventa.py ---



from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from ventas.models import DetalleVenta
from ventas.serializers import DetalleVentaSerializer
from accounts.permissions import IsVendedor, IsEmpresaAdmin
from rest_framework.pagination import PageNumberPagination
import django_filters

# Clase de paginación personalizada
class DetalleVentaPagination(PageNumberPagination):
    page_size = 10  # Número de resultados por página
    page_size_query_param = 'page_size'
    max_page_size = 100  # Máximo número de resultados por página

# Filtro personalizado para Detalles de Venta
class DetalleVentaFilter(django_filters.FilterSet):
    # Filtro por fecha de la venta
    fecha_inicio = django_filters.DateFilter(field_name='venta__fecha', lookup_expr='gte', label='Fecha desde')
    fecha_fin = django_filters.DateFilter(field_name='venta__fecha', lookup_expr='lte', label='Fecha hasta')

    class Meta:
        model = DetalleVenta
        fields = ['venta', 'producto', 'fecha_inicio', 'fecha_fin']

class DetalleVentaViewSet(viewsets.ModelViewSet):
    """
    CRUD para Detalles de Venta
    """
    queryset = DetalleVenta.objects.all().select_related('venta', 'producto')
    serializer_class = DetalleVentaSerializer
    permission_classes = [permissions.IsAuthenticated & (IsVendedor | IsEmpresaAdmin)]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = DetalleVentaFilter  # Filtro personalizado
    pagination_class = DetalleVentaPagination  # Paginación personalizada

    # Permitimos ordenar por cantidad y precio_unitario
    ordering_fields = ['cantidad', 'precio_unitario']
    ordering = ['-cantidad']  # Orden predeterminado por cantidad descendente

    def get_queryset(self):
        user = self.request.user
        if user.rol.nombre == "Superadministrador":
            return self.queryset
        # Filtrar detalles solo de ventas pertenecientes a la empresa del usuario
        return self.queryset.filter(venta__empresa=user.empresa)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)









# from rest_framework import viewsets, permissions
# from django_filters.rest_framework import DjangoFilterBackend
# from ventas.models import DetalleVenta
# from ventas.serializers import DetalleVentaSerializer
# from accounts.permissions import IsVendedor, IsEmpresaAdmin

# class DetalleVentaViewSet(viewsets.ModelViewSet):
#     """
#     CRUD para Detalles de Venta
#     """
#     queryset = DetalleVenta.objects.all().select_related('venta', 'producto')
#     serializer_class = DetalleVentaSerializer
#     permission_classes = [permissions.IsAuthenticated & (IsVendedor | IsEmpresaAdmin)]
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['venta', 'producto']

#     def get_queryset(self):
#         user = self.request.user
#         if user.rol.nombre == "Superadministrador":
#             return self.queryset
#         # Filtrar detalles solo de ventas pertenecientes a la empresa del usuario
#         return self.queryset.filter(venta__empresa=user.empresa)






# from rest_framework import viewsets, permissions
# from django_filters.rest_framework import DjangoFilterBackend
# from ventas.models import DetalleVenta
# from ventas.serializers import DetalleVentaSerializer
# from accounts.permissions import IsVendedor, IsEmpresaAdmin

# class DetalleVentaViewSet(viewsets.ModelViewSet):
#     """
#     CRUD para Detalles de Venta
#     """
#     queryset = DetalleVenta.objects.all().select_related('venta', 'producto')
#     serializer_class = DetalleVentaSerializer
#     permission_classes = [permissions.IsAuthenticated & (IsVendedor | IsEmpresaAdmin)]
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['venta', 'producto']


# --- /home/runner/workspace/ventas/views/dashboard.py ---
from rest_framework.views import APIView
from rest_framework.response import Response
from ventas.models import Venta, DetalleVenta
from inventario.models import Producto, Inventario, MovimientoInventario
from django.db.models import Sum, F, Count
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from datetime import timedelta
from django.utils import timezone

class VentaDashboardAPIView(APIView):
    """
    Vista para obtener estadísticas del dashboard de ventas.
    """

    def get(self, request, *args, **kwargs):
        # Obtener los parámetros 'fecha' y 'periodo' de la URL
        fecha_param = request.query_params.get('fecha')
        periodo_param = request.query_params.get('periodo', 'diario')  # El valor predeterminado es 'diario'

        # Si el parámetro 'fecha' es 'hoy', usamos la fecha actual
        if fecha_param == 'hoy':
            fecha_param = timezone.now().date()
        elif fecha_param:  # Si 'fecha_param' no es None o vacío
            # Intentamos usar la fecha proporcionada en formato 'YYYY-MM-DD'
            try:
                fecha_param = timezone.datetime.strptime(fecha_param, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": "Fecha no válida. Usa el formato YYYY-MM-DD o 'hoy'."})
        else:
            # Si no se pasa ninguna fecha, usamos la fecha actual
            fecha_param = timezone.now().date()

        # Filtramos las ventas por la fecha proporcionada
        ventas_filtradas = Venta.objects.filter(fecha__date=fecha_param)

        # Total de ventas
        total_ventas = ventas_filtradas.aggregate(total=Sum('total'))['total'] or 0

        # Ventas agrupadas por estado
        ventas_por_estado = ventas_filtradas.values('estado').annotate(total=Sum('total'))

        # Ventas por vendedor
        ventas_por_vendedor = ventas_filtradas.values('usuario__username').annotate(total=Sum('total'))

        # Promedio de ventas por transacción
        promedio_venta = ventas_filtradas.aggregate(promedio=Sum('total') / Count('id'))['promedio'] or 0

        # Ventas de los últimos 30 días
        fecha_limite = timezone.now() - timedelta(days=30)
        ventas_ultimos_30_dias = ventas_filtradas.filter(fecha__gte=fecha_limite).aggregate(total=Sum('total'))['total'] or 0

        # Top 5 productos más vendidos (en base a las ventas por detalle)
        top_productos = DetalleVenta.objects.filter(venta__fecha__date=fecha_param).values('producto__nombre').annotate(
            total_ventas=Sum(F('cantidad') * F('precio_unitario'))
        ).order_by('-total_ventas')[:5]

        # Ingresos y margen por producto (basado en costo y precio)
        ingresos_y_margen = DetalleVenta.objects.filter(venta__fecha__date=fecha_param).values('producto__nombre').annotate(
            total_ingresos=Sum(F('cantidad') * F('precio_unitario')),
            margen=Sum(F('cantidad') * (F('precio_unitario') - F('producto__precio_compra')))  # Cambio de costo a precio_compra
        ).order_by('-total_ingresos')[:5]

        # Ventas por cliente
        ventas_por_cliente = ventas_filtradas.values('cliente__nombre').annotate(total=Sum('total')).order_by('-total')[:5]

        # Calcular el stock disponible por producto
        stock_disponible = Inventario.objects.filter(
            producto__empresa__in=ventas_filtradas.values('empresa')
        ).values('producto__nombre').annotate(
            total_stock=Sum(F('cantidad')),
            stock_minimo=F('producto__stock_minimo')
        ).order_by('producto__nombre')

        # Identificar productos con bajo stock
        productos_bajo_stock = stock_disponible.filter(
            total_stock__lte=F('stock_minimo')
        ).order_by('total_stock')

        # Promedio de precio de venta y precio de compra por producto
        precios_promedio = Producto.objects.values('nombre').annotate(
            promedio_precio_venta=Sum('precio_venta') / Count('id'),
            promedio_precio_compra=Sum('precio_compra') / Count('id')
        )

        # Agrupación de ventas por periodo
        if periodo_param == 'semanal':
            ventas_por_periodo = ventas_filtradas.annotate(
                semana=TruncWeek('fecha')
            ).values('semana').annotate(total=Sum('total')).order_by('semana')

        elif periodo_param == 'mensual':
            ventas_por_periodo = ventas_filtradas.annotate(
                mes=TruncMonth('fecha')
            ).values('mes').annotate(total=Sum('total')).order_by('mes')

        else:  # Por defecto, agrupamos por día
            ventas_por_periodo = ventas_filtradas.annotate(
                dia=TruncDate('fecha')
            ).values('dia').annotate(total=Sum('total')).order_by('dia')

        # Devolviendo los resultados con stock y precios promedios
        return Response({
            "total_ventas": total_ventas,
            "ventas_por_estado": ventas_por_estado,
            "ventas_por_vendedor": ventas_por_vendedor,
            "promedio_venta": promedio_venta,
            "ventas_ultimos_30_dias": ventas_ultimos_30_dias,
            "top_productos": top_productos,
            "ingresos_y_margen": ingresos_y_margen,
            "ventas_por_cliente": ventas_por_cliente,
            "stock_disponible": stock_disponible,
            "productos_bajo_stock": productos_bajo_stock,
            "precios_promedio": precios_promedio,
            "ventas_por_periodo": ventas_por_periodo
        })











# from rest_framework.views import APIView
# from rest_framework.response import Response
# from ventas.models import Venta, DetalleVenta
# from inventario.models import Producto, Inventario, MovimientoInventario
# from django.db.models import Sum, F, Count, ExpressionWrapper, DecimalField
# from datetime import timedelta
# from django.utils import timezone


# class VentaDashboardAPIView(APIView):
#     """
#     Vista para obtener estadísticas del dashboard de ventas.
#     """

#     def get(self, request, *args, **kwargs):
#         # Obtener el parámetro 'fecha' de la URL, por ejemplo, "fecha__date=hoy"
#         fecha_param = request.query_params.get('fecha')

#         # Si el parámetro 'fecha' es 'hoy', usamos la fecha actual
#         if fecha_param == 'hoy':
#             fecha_param = timezone.now().date()
#         else:
#             # Si no, intentamos usar la fecha proporcionada en formato 'YYYY-MM-DD'
#             try:
#                 fecha_param = timezone.datetime.strptime(fecha_param, '%Y-%m-%d').date()
#             except ValueError:
#                 return Response({"error": "Fecha no válida. Usa el formato YYYY-MM-DD o 'hoy'."})

#         # Filtramos las ventas por la fecha proporcionada
#         ventas_filtradas = Venta.objects.filter(fecha__date=fecha_param)

#         # Total de ventas
#         total_ventas = ventas_filtradas.aggregate(total=Sum('total'))['total'] or 0

#         # Ventas agrupadas por estado
#         ventas_por_estado = ventas_filtradas.values('estado').annotate(total=Sum('total'))

#         # Ventas por vendedor
#         ventas_por_vendedor = ventas_filtradas.values('usuario__username').annotate(total=Sum('total'))

#         # Promedio de ventas por transacción
#         promedio_venta = ventas_filtradas.aggregate(promedio=Sum('total') / Count('id'))['promedio'] or 0

#         # Ventas de los últimos 30 días
#         fecha_limite = timezone.now() - timedelta(days=30)
#         ventas_ultimos_30_dias = ventas_filtradas.filter(fecha__gte=fecha_limite).aggregate(total=Sum('total'))['total'] or 0

#         # Top 5 productos más vendidos (en base a las ventas por detalle)
#         top_productos = DetalleVenta.objects.filter(venta__fecha__date=fecha_param).values('producto__nombre').annotate(
#             total_ventas=Sum(F('cantidad') * F('precio_unitario'))
#         ).order_by('-total_ventas')[:5]

#         # Ingresos y margen por producto (basado en costo y precio)
#         ingresos_y_margen = DetalleVenta.objects.filter(venta__fecha__date=fecha_param).values('producto__nombre').annotate(
#             total_ingresos=Sum(F('cantidad') * F('precio_unitario')),
#             margen=Sum(F('cantidad') * (F('precio_unitario') - F('producto__precio_compra')))  # Cambio de costo a precio_compra
#         ).order_by('-total_ingresos')[:5]

#         # Ventas por cliente
#         ventas_por_cliente = ventas_filtradas.values('cliente__nombre').annotate(total=Sum('total')).order_by('-total')[:5]

#         # Calcular el stock disponible por producto
#         stock_disponible = Inventario.objects.filter(
#             producto__empresa__in=ventas_filtradas.values('empresa')
#         ).values('producto__nombre').annotate(
#             total_stock=Sum(F('cantidad')),
#             stock_minimo=F('producto__stock_minimo')
#         ).order_by('producto__nombre')

#         # Identificar productos con bajo stock
#         productos_bajo_stock = stock_disponible.filter(
#             total_stock__lte=F('stock_minimo')
#         ).order_by('total_stock')

#         # Promedio de precio de venta y precio de compra por producto
#         precios_promedio = Producto.objects.values('nombre').annotate(
#             promedio_precio_venta=Sum('precio_venta') / Count('id'),
#             promedio_precio_compra=Sum('precio_compra') / Count('id')
#         )

#         # Devolviendo los resultados con stock y precios promedios
#         return Response({
#             "total_ventas": total_ventas,
#             "ventas_por_estado": ventas_por_estado,
#             "ventas_por_vendedor": ventas_por_vendedor,
#             "promedio_venta": promedio_venta,
#             "ventas_ultimos_30_dias": ventas_ultimos_30_dias,
#             "top_productos": top_productos,
#             "ingresos_y_margen": ingresos_y_margen,
#             "ventas_por_cliente": ventas_por_cliente,
#             "stock_disponible": stock_disponible,
#             "productos_bajo_stock": productos_bajo_stock,
#             "precios_promedio": precios_promedio
#         })





#from rest_framework.views import APIView
# from rest_framework.response import Response
# from ventas.models import Venta, DetalleVenta
# from django.db.models import Sum, Count
# from datetime import timedelta
# from django.utils import timezone

# class VentaDashboardAPIView(APIView):
#     """
#     Vista para obtener estadísticas del dashboard de ventas
#     """
#     def get(self, request, *args, **kwargs):
#         # Total de ventas
#         total_ventas = Venta.objects.aggregate(total=Sum('total'))['total'] or 0

#         # Ventas agrupadas por estado
#         ventas_por_estado = Venta.objects.values('estado').annotate(total=Sum('total'))

#         # Ventas por vendedor
#         ventas_por_vendedor = Venta.objects.values('usuario__username').annotate(total=Sum('total'))

#         # Promedio de ventas por transacción
#         promedio_venta = Venta.objects.aggregate(promedio=Sum('total') / Count('id'))['promedio'] or 0

#         # Ventas de los últimos 30 días
#         fecha_limite = timezone.now() - timedelta(days=30)
#         ventas_ultimos_30_dias = Venta.objects.filter(fecha__gte=fecha_limite).aggregate(total=Sum('total'))['total'] or 0

#         # Top 5 productos más vendidos (en base a las ventas por detalle)
#         top_productos = DetalleVenta.objects.values('producto__nombre').annotate(total_ventas=Sum('total')).order_by('-total_ventas')[:5]

#         # Ingresos y margen por producto (basado en costo y precio)
#         ingresos_y_margen = DetalleVenta.objects.values('producto__nombre').annotate(
#             total_ingresos=Sum('total'),
#             margen=Sum('total') - Sum('producto__costo')  # Suponiendo que cada detalle tiene un campo de costo
#         ).order_by('-total_ingresos')[:5]

#         # Ventas por cliente
#         ventas_por_cliente = Venta.objects.values('cliente__nombre').annotate(total=Sum('total')).order_by('-total')[:5]

#         # Ventas diarias (Ventas por día)
#         hoy = timezone.now().date()
#         ventas_diarias = Venta.objects.filter(fecha__date=hoy).aggregate(total=Sum('total'))['total'] or 0

#         # Ventas mensuales (Ventas del mes actual)
#         inicio_mes = hoy.replace(day=1)
#         ventas_mensuales = Venta.objects.filter(fecha__gte=inicio_mes).aggregate(total=Sum('total'))['total'] or 0

#         # Devolviendo los resultados
#         return Response({
#             "total_ventas": total_ventas,
#             "ventas_por_estado": ventas_por_estado,
#             "ventas_por_vendedor": ventas_por_vendedor,
#             "promedio_venta": promedio_venta,
#             "ventas_ultimos_30_dias": ventas_ultimos_30_dias,
#             "top_productos": top_productos,
#             "ingresos_y_margen": ingresos_y_margen,
#             "ventas_por_cliente": ventas_por_cliente,
#             "ventas_diarias": ventas_diarias,
#             "ventas_mensuales": ventas_mensuales
#         })


# from rest_framework import viewsets, permissions, filters
# from django_filters.rest_framework import DjangoFilterBackend
# from ventas.models import Venta
# from ventas.serializers import VentaSerializer
# from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsVendedor
# import django_filters
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.response import Response


# # Filtros personalizados para las ventas
# class VentaFilter(django_filters.FilterSet):
#     # Filtro para el RFC del cliente
#     rfc_cliente = django_filters.CharFilter(field_name='cliente__rfc', lookup_expr='icontains', label='RFC del Cliente')

#     # Filtro para el nombre del producto (en los detalles de la venta)
#     nombre_producto = django_filters.CharFilter(field_name='detalles__producto__nombre', lookup_expr='icontains', label='Nombre del Producto')

#     # Filtros de fecha (rango de fechas)
#     fecha_inicio = django_filters.DateFilter(field_name='fecha', lookup_expr='gte', label='Fecha desde')
#     fecha_fin = django_filters.DateFilter(field_name='fecha', lookup_expr='lte', label='Fecha hasta')

#     # Filtro para el vendedor
#     vendedor = django_filters.CharFilter(field_name='usuario__username', lookup_expr='icontains', label='Vendedor')

#     # Filtro para el estado de la venta
#     estado = django_filters.ChoiceFilter(choices=Venta.ESTADO_CHOICES, label='Estado')

#     class Meta:
#         model = Venta
#         fields = ['empresa', 'estado', 'cliente', 'fecha_inicio', 'fecha_fin', 'rfc_cliente', 'nombre_producto', 'vendedor']


# # Clase de paginación personalizada
# class VentaPagination(PageNumberPagination):
#     page_size = 10  # Número de resultados por página
#     page_size_query_param = 'page_size'
#     max_page_size = 100  # Máximo número de resultados por página


# class VentaViewSet(viewsets.ModelViewSet):
#     """
#     CRUD para Ventas, con detalles anidados.
#     """
#     queryset = Venta.objects.all().select_related('cliente', 'usuario', 'empresa').prefetch_related('detalles__producto')
#     serializer_class = VentaSerializer
#     permission_classes = [permissions.IsAuthenticated & (IsSuperAdmin | IsEmpresaAdmin | IsVendedor)]
#     filter_backends = [filters.SearchFilter, DjangoFilterBackend]
#     search_fields = ['cliente__nombre', 'usuario__username', 'estado']
#     filterset_class = VentaFilter  # Usamos el filtro personalizado aquí

#     # Configuramos la paginación
#     pagination_class = VentaPagination

#     # Ordenamiento por fecha o total
#     ordering_fields = ['fecha', 'total']  # Permite ordenar por fecha y total
#     ordering = ['-fecha']  # Orden por defecto: por fecha descendente

#     def get_queryset(self):
#         user = self.request.user
#         if user.rol.nombre == "Superadministrador":
#             return self.queryset
#         return self.queryset.filter(empresa=user.empresa)

#     def perform_create(self, serializer):
#         serializer.save(usuario=self.request.user)

#     def get_latest_sales(self):
#         """
#         Devuelve las últimas n ventas con filtros aplicados.
#         """
#         n = self.request.query_params.get('n', 10)  # Número de ventas a devolver
#         try:
#             n = int(n)
#         except ValueError:
#             n = 10  # Si no se pasa un número válido, devolver las últimas 10 ventas

#         # Filtrar las ventas según los parámetros de búsqueda
#         filtered_sales = self.filter_queryset(self.queryset.order_by('-fecha')[:n])

#         # Devuelve las ventas filtradas y limitadas
#         return filtered_sales

#     def list(self, request, *args, **kwargs):
#         """
#         Sobrescribimos el método `list` para agregar soporte para obtener las últimas 'n' ventas.
#         """
#         # Si se pasa el parámetro 'latest', devolver solo las últimas 'n' ventas
#         if 'latest' in self.request.query_params:
#             latest_sales = self.get_latest_sales()
#             page = self.paginate_queryset(latest_sales)
#             if page is not None:
#                 serializer = self.get_serializer(page, many=True)
#                 return self.get_paginated_response(serializer.data)
#             return Response(self.get_serializer(latest_sales, many=True).data)

#         # Si no se pide 'latest', proceder con la lógica predeterminada
#         return super().list(request, *args, **kwargs)



# --- /home/runner/workspace/ventas/views/clientes.py ---
# ventas/views/clientes.py
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from ventas.models import Cliente
from ventas.serializers import ClienteSerializer
from ventas.filters.clientes import ClienteFilter  # 👈 Filtro avanzado para Clientes
from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsVendedor  # 👈 Permisos personalizados

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().select_related('empresa')
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated & (IsSuperAdmin | IsEmpresaAdmin | IsVendedor)]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'rfc', 'correo', 'telefono']
    filterset_class = ClienteFilter

    def get_queryset(self):
        user = self.request.user
        if user.rol.nombre == "Superadministrador":
            # Superadmin ve todos los clientes
            return self.queryset
        else:
            # Los demás solo clientes de su empresa
            return self.queryset.filter(empresa=user.empresa)



# --- /home/runner/workspace/ventas/views/ventas.py ---
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from ventas.models import Venta
from ventas.serializers import VentaSerializer
from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsVendedor
import django_filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# Filtros personalizados para las ventas
class VentaFilter(django_filters.FilterSet):
    # Filtro para el RFC del cliente
    rfc_cliente = django_filters.CharFilter(field_name='cliente__rfc', lookup_expr='icontains', label='RFC del Cliente')

    # Filtro para el nombre del producto (en los detalles de la venta)
    nombre_producto = django_filters.CharFilter(field_name='detalles__producto__nombre', lookup_expr='icontains', label='Nombre del Producto')

    # Filtros de fecha (rango de fechas)
    fecha_inicio = django_filters.DateFilter(field_name='fecha', lookup_expr='gte', label='Fecha desde')
    fecha_fin = django_filters.DateFilter(field_name='fecha', lookup_expr='lte', label='Fecha hasta')

    # Filtro para el vendedor
    vendedor = django_filters.CharFilter(field_name='usuario__username', lookup_expr='icontains', label='Vendedor')

    # Filtro para el estado de la venta
    estado = django_filters.ChoiceFilter(choices=Venta.ESTADO_CHOICES, label='Estado')

    class Meta:
        model = Venta
        fields = ['empresa', 'estado', 'cliente', 'fecha_inicio', 'fecha_fin', 'rfc_cliente', 'nombre_producto', 'vendedor']


# Clase de paginación personalizada
class VentaPagination(PageNumberPagination):
    page_size = 10  # Número de resultados por página
    page_size_query_param = 'page_size'
    max_page_size = 100  # Máximo número de resultados por página


class VentaViewSet(viewsets.ModelViewSet):
    """
    CRUD para Ventas, con detalles anidados.
    """
    queryset = Venta.objects.all().select_related('cliente', 'usuario', 'empresa').prefetch_related('detalles__producto')
    serializer_class = VentaSerializer
    permission_classes = [permissions.IsAuthenticated & (IsSuperAdmin | IsEmpresaAdmin | IsVendedor)]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['cliente__nombre', 'usuario__username', 'estado']
    filterset_class = VentaFilter  # Usamos el filtro personalizado aquí

    # Configuramos la paginación
    pagination_class = VentaPagination

    # Ordenamiento por fecha o total
    ordering_fields = ['fecha', 'total']  # Permite ordenar por fecha y total
    ordering = ['-fecha']  # Orden por defecto: por fecha descendente

    def get_queryset(self):
        user = self.request.user
        if user.rol.nombre == "Superadministrador":
            return self.queryset
        return self.queryset.filter(empresa=user.empresa)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def get_latest_sales(self):
        """
        Devuelve las últimas n ventas con filtros aplicados.
        """
        n = self.request.query_params.get('n', 10)  # Número de ventas a devolver
        try:
            n = int(n)
        except ValueError:
            n = 10  # Si no se pasa un número válido, devolver las últimas 10 ventas

        # Filtrar las ventas según los parámetros de búsqueda
        filtered_sales = self.filter_queryset(self.queryset.order_by('-fecha')[:n])

        # Devuelve las ventas filtradas y limitadas
        return filtered_sales

    def list(self, request, *args, **kwargs):
        """
        Sobrescribimos el método `list` para agregar soporte para obtener las últimas 'n' ventas.
        """
        # Si se pasa el parámetro 'latest', devolver solo las últimas 'n' ventas
        if 'latest' in self.request.query_params:
            latest_sales = self.get_latest_sales()
            page = self.paginate_queryset(latest_sales)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            return Response(self.get_serializer(latest_sales, many=True).data)

        # Si no se pide 'latest', proceder con la lógica predeterminada
        return super().list(request, *args, **kwargs)



