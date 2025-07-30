
# --- /home/runner/workspace/finanzas/__init__.py ---



# --- /home/runner/workspace/finanzas/admin.py ---
from django.contrib import admin

# Register your models here.



# --- /home/runner/workspace/finanzas/constants.py ---
# finanzas/constants.py (nuevo archivo)
ESTADO_CUENTA_CHOICES = [
    ('PENDIENTE', 'Pendiente'),
    ('PAGADO', 'Pagado'),
    ('VENCIDO', 'Vencido'),
]


# --- /home/runner/workspace/finanzas/utils.py ---
# finanzas/utils.py
from django.utils.timezone import now
from datetime import timedelta
from finanzas.models import CuentaPorCobrar

def cuentas_por_vencer():
    hoy = now().date()
    limite = hoy + timedelta(days=3)
    return CuentaPorCobrar.objects.filter(fecha_vencimiento__range=(hoy, limite), estado='PENDIENTE')



# --- /home/runner/workspace/finanzas/urls.py ---
# finanzas/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from finanzas.views.cuentas_por_cobrar import CuentaPorCobrarViewSet
from finanzas.views.cuentas_por_pagar import CuentaPorPagarViewSet
from finanzas.views.pagos import PagoViewSet
from finanzas.views.reportes import (
    CuentasPorCobrarVencidasView,
    FlujoDeCajaView,
    AnalisisPorClienteProveedorView,
    CuentasPorCobrarAvanzadasView,
    FlujoDeCajaProyectadoView,
    RentabilidadClienteProveedorView,
    CicloConversionEfectivoView,
    LiquidezCorrienteView,
)

# Configura el router para las vistas generales de los modelos
router = DefaultRouter()
router.register(r'cuentas_por_pagar', CuentaPorPagarViewSet, basename='cuentas_por_pagar')
router.register(r'cuentas_por_cobrar', CuentaPorCobrarViewSet, basename='cuentas_por_cobrar')
router.register(r'pagos', PagoViewSet, basename='pagos')



urlpatterns = [
    path('reports/overdue_accounts_receivable/', CuentasPorCobrarVencidasView.as_view(), name='overdue_accounts_receivable'),
    path('reports/cash_flow/', FlujoDeCajaView.as_view(), name='cash_flow'),
    path('reports/customer_supplier_analysis/', AnalisisPorClienteProveedorView.as_view(), name='customer_supplier_analysis'),
    path('reports/advanced_accounts_receivable/', CuentasPorCobrarAvanzadasView.as_view(), name='advanced_accounts_receivable'),
    path('reports/projected_cash_flow/', FlujoDeCajaProyectadoView.as_view(), name='projected_cash_flow'),
    path('reports/customer_supplier_profitability/', RentabilidadClienteProveedorView.as_view(), name='customer_supplier_profitability'),
    path('reports/cash_conversion_cycle/', CicloConversionEfectivoView.as_view(), name='cash_conversion_cycle'),
    path('reports/current_liquidity/', LiquidezCorrienteView.as_view(), name='current_liquidity'),
]

# Incluir las rutas del router (esto es para las vistas de los modelos)
urlpatterns += router.urls



# --- /home/runner/workspace/finanzas/apps.py ---
from django.apps import AppConfig

class FinanzasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finanzas'

    def ready(self):
        import finanzas.signals


# --- /home/runner/workspace/finanzas/models.py ---
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db.models import TextChoices
from django.utils.timezone import now
from core.models import Empresa
from ventas.models import Venta
from compras.models import Compra
from accounts.models import Usuario



# ──────────────────────────────────────
# ENUMS: Estados y Métodos de Pago
# ──────────────────────────────────────

class EstadoCuentaChoices(TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    PAGADO = 'PAGADO', 'Pagado'
    VENCIDO = 'VENCIDO', 'Vencido'


class MetodoPagoChoices(TextChoices):
    EFECTIVO = 'EFECTIVO', 'Efectivo'
    TARJETA = 'TARJETA', 'Tarjeta'
    TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia'
    CHEQUE = 'CHEQUE', 'Cheque'
    OTRO = 'OTRO', 'Otro'


# ──────────────────────────────
# Modelo: Cuenta por Cobrar
# ──────────────────────────────

class CuentaPorCobrar(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='cuentas_por_cobrar', default=4)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='cuentas_por_cobrar')
    monto = models.DecimalField(max_digits=14, decimal_places=2)
    fecha_vencimiento = models.DateField()
    estado = models.CharField(max_length=10, choices=EstadoCuentaChoices.choices, default=EstadoCuentaChoices.PENDIENTE)
    notas = models.TextField(blank=True, null=True)

    def clean(self):
        if self.monto <= 0:
            raise ValidationError("El monto debe ser mayor a cero.")
        if self.fecha_vencimiento < timezone.now().date():
            raise ValidationError("La fecha de vencimiento no puede estar en el pasado.")

    @property
    def monto_pagado(self):
        return self.pagos.aggregate(total=Sum('monto'))['total'] or 0

    @property
    def saldo_pendiente(self):
        return round(self.monto - self.monto_pagado, 2)

    def actualizar_estado(self):
        if self.saldo_pendiente <= 0:
            self.estado = EstadoCuentaChoices.PAGADO
        elif self.fecha_vencimiento < timezone.now().date():
            self.estado = EstadoCuentaChoices.VENCIDO
        else:
            self.estado = EstadoCuentaChoices.PENDIENTE
        self.save()

    class Meta:
        verbose_name = "Cuenta por Cobrar"
        verbose_name_plural = "Cuentas por Cobrar"
        ordering = ['fecha_vencimiento']
        indexes = [
            models.Index(fields=['fecha_vencimiento', 'estado']),
            models.Index(fields=['venta']),
        ]

    def __str__(self):
        return f"CxC Venta #{self.venta.id} - {self.estado} - ${self.monto}"


# ──────────────────────────────
# Modelo: Cuenta por Pagar
# ──────────────────────────────

class CuentaPorPagar(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='cuentas_por_pagar', default=4)
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='cuentas_por_pagar')
    monto = models.DecimalField(max_digits=14, decimal_places=2)
    fecha_vencimiento = models.DateField()
    estado = models.CharField(max_length=10, choices=EstadoCuentaChoices.choices, default=EstadoCuentaChoices.PENDIENTE)
    notas = models.TextField(blank=True, null=True)

    def clean(self):
        if self.monto <= 0:
            raise ValidationError("El monto debe ser mayor a cero.")
        if self.fecha_vencimiento < timezone.now().date():
            raise ValidationError("La fecha de vencimiento no puede estar en el pasado.")

    @property
    def monto_pagado(self):
        return self.pagos.aggregate(total=Sum('monto'))['total'] or 0

    @property
    def saldo_pendiente(self):
        return round(self.monto - self.monto_pagado, 2)

    def actualizar_estado(self):
        if self.saldo_pendiente <= 0:
            self.estado = EstadoCuentaChoices.PAGADO
        elif self.fecha_vencimiento < timezone.now().date():
            self.estado = EstadoCuentaChoices.VENCIDO
        else:
            self.estado = EstadoCuentaChoices.PENDIENTE
        self.save()

    class Meta:
        verbose_name = "Cuenta por Pagar"
        verbose_name_plural = "Cuentas por Pagar"
        ordering = ['fecha_vencimiento']
        indexes = [
            models.Index(fields=['fecha_vencimiento', 'estado']),
            models.Index(fields=['compra']),
        ]

    def __str__(self):
        return f"CxP Compra #{self.compra.id} - {self.estado} - ${self.monto}"


# ──────────────────────────────
# Modelo: Pago (CxC o CxP)
# ──────────────────────────────

def hoy_fecha():
    return now().date()

class Pago(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='pagos', default=4)
    cuenta_cobrar = models.ForeignKey(CuentaPorCobrar, on_delete=models.CASCADE, null=True, blank=True, related_name='pagos')
    cuenta_pagar = models.ForeignKey(CuentaPorPagar, on_delete=models.CASCADE, null=True, blank=True, related_name='pagos')
    monto = models.DecimalField(max_digits=14, decimal_places=2)
    fecha = models.DateField(default=hoy_fecha)
    metodo_pago = models.CharField(max_length=20, choices=MetodoPagoChoices.choices)
    observaciones = models.TextField(blank=True, null=True)
    comprobante = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    asiento_contable_creado = models.BooleanField(default=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        if self.monto <= 0:
            raise ValidationError("El monto del pago debe ser mayor a cero.")
        if not self.cuenta_cobrar and not self.cuenta_pagar:
            raise ValidationError("El pago debe estar vinculado a una cuenta por cobrar o por pagar.")
        if self.cuenta_cobrar and self.cuenta_pagar:
            raise ValidationError("Un pago no puede estar vinculado a ambas cuentas a la vez.")

        # Verificación de que el pago no exceda el saldo pendiente de la cuenta
        if self.cuenta_cobrar:
            if self.monto > self.cuenta_cobrar.saldo_pendiente:
                raise ValidationError("El monto del pago excede el saldo pendiente de la cuenta por cobrar.")
        if self.cuenta_pagar:
            if self.monto > self.cuenta_pagar.saldo_pendiente:
                raise ValidationError("El monto del pago excede el saldo pendiente de la cuenta por pagar.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Asegura que las validaciones del modelo se ejecuten antes de guardar
        super().save(*args, **kwargs)
        if self.cuenta_cobrar:
            self.cuenta_cobrar.actualizar_estado()
        if self.cuenta_pagar:
            self.cuenta_pagar.actualizar_estado()

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['metodo_pago']),
        ]

    def __str__(self):
        cuenta = 'CxC' if self.cuenta_cobrar else 'CxP'
        referencia = self.cuenta_cobrar_id or self.cuenta_pagar_id or 'N/A'
        return f"Pago {cuenta} #{referencia} - ${self.monto} - {self.fecha}"




# --- /home/runner/workspace/finanzas/signals.py ---
# finanzas/signals.py

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from finanzas.models import Pago
from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable
from django.core.exceptions import ObjectDoesNotExist

# -------------------------
# Eliminar Asiento al borrar un Pago
# -------------------------

@receiver(post_delete, sender=Pago)
def eliminar_asiento_al_eliminar_pago(sender, instance, **kwargs):
    try:
        AsientoContable.objects.filter(
            referencia_id=instance.id,
            referencia_tipo='Pago',
            empresa=instance.empresa
        ).delete()
    except Exception as e:
        print(f"❌ Error eliminando asiento contable al borrar pago: {e}")


# -------------------------
# Crear Asiento al crear un Pago
# -------------------------

@receiver(post_save, sender=Pago)
def crear_asiento_para_pago(sender, instance, created, **kwargs):
    if not created or instance.asiento_contable_creado:
        return  # Evita duplicados

    try:
        # Buscar cuentas contables relacionadas al pago
        banco_cuenta = CuentaContable.objects.get(codigo='1020', empresa=instance.empresa)
        gasto_cuenta = CuentaContable.objects.get(codigo='6000', empresa=instance.empresa)
    except ObjectDoesNotExist as e:
        print(f"❌ Error: cuenta contable no encontrada: {e}")
        return

    try:
        # Crear asiento contable
        asiento = AsientoContable.objects.create(
            empresa=instance.empresa,
            fecha=instance.fecha,
            concepto=f'Pago automático #{instance.id}',
            usuario=instance.usuario,
            conciliado=False,
            referencia_id=instance.id,
            referencia_tipo='Pago',
            total_debe=instance.monto,
            total_haber=instance.monto,
            es_automatico=True,
        )

        # Cargar detalle del asiento (Banco - Haber)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=banco_cuenta,
            debe=0,
            haber=instance.monto,
            descripcion='Salida de dinero (Pago)'
        )

        # Cargar detalle del asiento (Gasto - Debe)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=gasto_cuenta,
            debe=instance.monto,
            haber=0,
            descripcion='Gasto generado por el pago'
        )

        # Marcar pago como ya registrado contablemente
        instance.asiento_contable_creado = True
        instance.save(update_fields=["asiento_contable_creado"])

    except Exception as e:
        print(f"❌ Error creando asiento contable para el pago: {e}")




# # finanzas/signals.py
# from django.db.models.signals import post_delete
# from django.dispatch import receiver
# from finanzas.models import Pago
# from contabilidad.models import AsientoContable

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from finanzas.models import Pago
# from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable

# @receiver(post_delete, sender=Pago)
# def eliminar_asiento_al_eliminar_pago(sender, instance, **kwargs):
#     try:
#         AsientoContable.objects.filter(
#             referencia_id=instance.id,
#             referencia_tipo='Pago',
#             empresa=instance.empresa
#         ).delete()
#     except Exception as e:
#         print(f"Error eliminando asiento contable al borrar pago: {e}")



# @receiver(post_save, sender=Pago)
# def crear_asiento_para_pago(sender, instance, created, **kwargs):
#     if not created or instance.asiento_contable_creado:
#         return  # Evitar duplicados

#     banco_cuenta = CuentaContable.objects.get(codigo='1020')  # Ejemplo: Banco
#     gasto_cuenta = CuentaContable.objects.get(codigo='6000')  # Ejemplo: Gasto general

#     asiento = AsientoContable.objects.create(
#         empresa=instance.empresa,
#         fecha=instance.fecha,
#         concepto=f'Pago automático #{instance.id}',
#         usuario=instance.usuario,
#         conciliado=False,
#         referencia_id=instance.id,
#         referencia_tipo='Pago',
#         total_debe=instance.monto,
#         total_haber=instance.monto,
#         es_automatico=True,
#     )

#     DetalleAsiento.objects.create(
#         asiento=asiento,
#         cuenta_contable=banco_cuenta,
#         debe=0,
#         haber=instance.monto,
#         descripcion='Salida de dinero (Pago)'
#     )

#     DetalleAsiento.objects.create(
#         asiento=asiento,
#         cuenta_contable=gasto_cuenta,
#         debe=instance.monto,
#         haber=0,
#         descripcion='Gasto generado por el pago'
#     )

#     # Marcar que ya fue generado para evitar duplicados
#     instance.asiento_contable_creado = True
#     instance.save(update_fields=["asiento_contable_creado"])



# --- /home/runner/workspace/finanzas/migrations/__init__.py ---



# --- /home/runner/workspace/finanzas/migrations/0001_initial.py ---
# Generated by Django 5.2.4 on 2025-07-30 17:07

import django.db.models.deletion
import finanzas.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('compras', '0001_initial'),
        ('core', '0001_initial'),
        ('ventas', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CuentaPorCobrar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=14)),
                ('fecha_vencimiento', models.DateField()),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('PAGADO', 'Pagado'), ('VENCIDO', 'Vencido')], default='PENDIENTE', max_length=10)),
                ('notas', models.TextField(blank=True, null=True)),
                ('empresa', models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, related_name='cuentas_por_cobrar', to='core.empresa')),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cuentas_por_cobrar', to='ventas.venta')),
            ],
            options={
                'verbose_name': 'Cuenta por Cobrar',
                'verbose_name_plural': 'Cuentas por Cobrar',
                'ordering': ['fecha_vencimiento'],
            },
        ),
        migrations.CreateModel(
            name='CuentaPorPagar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=14)),
                ('fecha_vencimiento', models.DateField()),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('PAGADO', 'Pagado'), ('VENCIDO', 'Vencido')], default='PENDIENTE', max_length=10)),
                ('notas', models.TextField(blank=True, null=True)),
                ('compra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cuentas_por_pagar', to='compras.compra')),
                ('empresa', models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, related_name='cuentas_por_pagar', to='core.empresa')),
            ],
            options={
                'verbose_name': 'Cuenta por Pagar',
                'verbose_name_plural': 'Cuentas por Pagar',
                'ordering': ['fecha_vencimiento'],
            },
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=14)),
                ('fecha', models.DateField(default=finanzas.models.hoy_fecha)),
                ('metodo_pago', models.CharField(choices=[('EFECTIVO', 'Efectivo'), ('TARJETA', 'Tarjeta'), ('TRANSFERENCIA', 'Transferencia'), ('CHEQUE', 'Cheque'), ('OTRO', 'Otro')], max_length=20)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('comprobante', models.FileField(blank=True, null=True, upload_to='comprobantes/')),
                ('asiento_contable_creado', models.BooleanField(default=False)),
                ('cuenta_cobrar', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='finanzas.cuentaporcobrar')),
                ('cuenta_pagar', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='finanzas.cuentaporpagar')),
                ('empresa', models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='core.empresa')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Pago',
                'verbose_name_plural': 'Pagos',
                'ordering': ['-fecha'],
            },
        ),
        migrations.AddIndex(
            model_name='cuentaporcobrar',
            index=models.Index(fields=['fecha_vencimiento', 'estado'], name='finanzas_cu_fecha_v_ed0862_idx'),
        ),
        migrations.AddIndex(
            model_name='cuentaporcobrar',
            index=models.Index(fields=['venta'], name='finanzas_cu_venta_i_fcf135_idx'),
        ),
        migrations.AddIndex(
            model_name='cuentaporpagar',
            index=models.Index(fields=['fecha_vencimiento', 'estado'], name='finanzas_cu_fecha_v_ec0010_idx'),
        ),
        migrations.AddIndex(
            model_name='cuentaporpagar',
            index=models.Index(fields=['compra'], name='finanzas_cu_compra__fb090c_idx'),
        ),
        migrations.AddIndex(
            model_name='pago',
            index=models.Index(fields=['fecha'], name='finanzas_pa_fecha_24441f_idx'),
        ),
        migrations.AddIndex(
            model_name='pago',
            index=models.Index(fields=['metodo_pago'], name='finanzas_pa_metodo__d75da5_idx'),
        ),
    ]



# --- /home/runner/workspace/finanzas/views/__init_.py ---
from .cuentas_por_pagar import CuentaPorPagarViewSet
from .cuentas_por_cobrar import CuentaPorCobrarViewSet
from .pagos import PagoViewSet

__all__ = [
    "CuentaPorPagarViewSet",
    "CuentaPorCobrarViewSet",
    "PagoViewSet",
]


# --- /home/runner/workspace/finanzas/views/cuentas_por_cobrar.py ---
from finanzas.models import CuentaPorCobrar
from finanzas.serializers import CuentaPorCobrarSerializer
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

class CuentaPorCobrarViewSet(viewsets.ModelViewSet):
    """
    Listar cuentas por cobrar con filtros por cliente, estado y fecha de vencimiento.
    """
    queryset = CuentaPorCobrar.objects.select_related('venta__cliente').all()
    serializer_class = CuentaPorCobrarSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['venta__cliente__nombre']
    ordering_fields = ['fecha_vencimiento', 'estado']
    ordering = ['fecha_vencimiento']

    def get_queryset(self):
        qs = super().get_queryset()
        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        fecha = self.request.query_params.get('fecha_vencimiento')
        if fecha:
            qs = qs.filter(fecha_vencimiento=fecha)
        return qs



# --- /home/runner/workspace/finanzas/views/cuentas_por_pagar.py ---
from rest_framework import viewsets, filters
from finanzas.models import CuentaPorPagar
from finanzas.serializers import CuentaPorPagarSerializer
from rest_framework.permissions import IsAuthenticated

class CuentaPorPagarViewSet(viewsets.ModelViewSet):
    """
    Listar cuentas por pagar con filtros por proveedor, estado y fecha de vencimiento.
    """
    queryset = CuentaPorPagar.objects.select_related('compra__proveedor').all()
    serializer_class = CuentaPorPagarSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['compra__proveedor__nombre']
    ordering_fields = ['fecha_vencimiento', 'estado']
    ordering = ['fecha_vencimiento']

    def get_queryset(self):
        qs = super().get_queryset()
        # Filtrar por estado
        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        # Filtrar por fecha_vencimiento (fecha exacta o rango?)
        fecha = self.request.query_params.get('fecha_vencimiento')
        if fecha:
            qs = qs.filter(fecha_vencimiento=fecha)
        return qs



# --- /home/runner/workspace/finanzas/views/reportes.py ---
from django.db.models import Sum, Count
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import date, timedelta
from django.db.models.functions import TruncMonth
from django.db.models import Avg, F, ExpressionWrapper, DurationField
from rest_framework.exceptions import ValidationError
from finanzas.models import (
    Pago,
    Venta,
    CuentaPorCobrar,
    CuentaPorPagar,
    Compra,
)


class CuentasPorCobrarVencidasView(APIView):
    def get(self, request):
        empresa_id = request.query_params.get('empresa')
        sucursal_id = request.query_params.get('sucursal')
        cliente_id = request.query_params.get('cliente')
        fecha_limite = request.query_params.get('fecha_limite') or date.today()

        cuentas = CuentaPorCobrar.objects.filter(estado='PENDIENTE', fecha_vencimiento__lte=fecha_limite)

        if empresa_id:
            cuentas = cuentas.filter(venta__empresa_id=empresa_id)
        if sucursal_id:
            cuentas = cuentas.filter(venta__sucursal_id=sucursal_id)
        if cliente_id:
            cuentas = cuentas.filter(cliente_id=cliente_id)

        total = cuentas.aggregate(total=Sum('monto'))['total'] or 0
        return Response({"cuentas_por_cobrar_vencidas": total})
        

class FlujoDeCajaView(APIView):
    def get(self, request):
        empresa_id = request.query_params.get('empresa')
        sucursal_id = request.query_params.get('sucursal')

        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')

        if fecha_inicio_str and fecha_fin_str:
            try:
                fecha_inicio = parse_date(fecha_inicio_str)
                fecha_fin = parse_date(fecha_fin_str)
                if not fecha_inicio or not fecha_fin:
                    raise ValueError
            except Exception:
                raise ValidationError("Los parámetros 'fecha_inicio' y 'fecha_fin' deben tener formato YYYY-MM-DD.")
        else:
            fecha_inicio = fecha_fin = None

        ingresos = Pago.objects.filter(cuenta_cobrar__isnull=False)
        egresos = Pago.objects.filter(cuenta_pagar__isnull=False)

        if empresa_id:
            ingresos = ingresos.filter(empresa_id=empresa_id)
            egresos = egresos.filter(empresa_id=empresa_id)
        if sucursal_id:
            ingresos = ingresos.filter(sucursal_id=sucursal_id)
            egresos = egresos.filter(sucursal_id=sucursal_id)
        if fecha_inicio and fecha_fin:
            ingresos = ingresos.filter(fecha__range=[fecha_inicio, fecha_fin])
            egresos = egresos.filter(fecha__range=[fecha_inicio, fecha_fin])

        total_ingresos = ingresos.aggregate(total=Sum('monto'))['total'] or 0
        total_egresos = egresos.aggregate(total=Sum('monto'))['total'] or 0

        return Response({
            "ingresos": total_ingresos,
            "egresos": total_egresos,
            "flujo_neto": total_ingresos - total_egresos
        })


class AnalisisPorClienteProveedorView(APIView):
    def get(self, request):
        cliente_id = request.query_params.get('cliente')
        proveedor_id = request.query_params.get('proveedor')

        # Validar que los parámetros de fecha sean strings antes de parsearlos
        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')

        fecha_inicio = parse_date(fecha_inicio_str) if fecha_inicio_str else None
        fecha_fin = parse_date(fecha_fin_str) if fecha_fin_str else None

        ventas = Venta.objects.all()
        compras = Compra.objects.all()

        if cliente_id:
            ventas = ventas.filter(cliente_id=cliente_id)
        if proveedor_id:
            compras = compras.filter(proveedor_id=proveedor_id)
        if fecha_inicio and fecha_fin:
            ventas = ventas.filter(fecha__range=[fecha_inicio, fecha_fin])
            compras = compras.filter(fecha__range=[fecha_inicio, fecha_fin])

        total_ventas = ventas.aggregate(total=Sum('total'))['total'] or 0
        total_compras = compras.aggregate(total=Sum('total'))['total'] or 0

        return Response({
            "ventas_cliente": total_ventas,
            "compras_proveedor": total_compras
        })


class CuentasPorCobrarAvanzadasView(APIView):
    def get(self, request):
        empresa_id = request.query_params.get('empresa')
        sucursal_id = request.query_params.get('sucursal')
        cliente_id = request.query_params.get('cliente')

        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')

        fecha_inicio = parse_date(fecha_inicio_str) if isinstance(fecha_inicio_str, str) else None
        fecha_fin = parse_date(fecha_fin_str) if isinstance(fecha_fin_str, str) else None

        cxc = CuentaPorCobrar.objects.all()

        if empresa_id:
            cxc = cxc.filter(venta__empresa_id=empresa_id)
        if sucursal_id:
            cxc = cxc.filter(venta__sucursal_id=sucursal_id)
        if cliente_id:
            cxc = cxc.filter(cliente_id=cliente_id)
        if fecha_inicio and fecha_fin:
            cxc = cxc.filter(fecha__range=[fecha_inicio, fecha_fin])

        total = cxc.aggregate(total=Sum('monto'))['total'] or 0
        return Response({"cuentas_por_cobrar": total})


class FlujoDeCajaProyectadoView(APIView):
    def get(self, request):
        empresa_id = request.query_params.get('empresa')

        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')

        fecha_inicio = parse_date(fecha_inicio_str) if isinstance(fecha_inicio_str, str) else None
        fecha_fin = parse_date(fecha_fin_str) if isinstance(fecha_fin_str, str) else None


        pagos = Pago.objects.all()

        if empresa_id:
            pagos = pagos.filter(empresa_id=empresa_id)
        if fecha_inicio and fecha_fin:
            pagos = pagos.filter(fecha__range=[fecha_inicio, fecha_fin])

        proyeccion = pagos.annotate(mes=TruncMonth('fecha')).values('mes').annotate(total=Sum('monto')).order_by('mes')

        return Response({"flujo_proyectado": proyeccion})



class RentabilidadClienteProveedorView(APIView):
    def get(self, request):
        cliente_id = request.query_params.get('cliente')
        proveedor_id = request.query_params.get('proveedor')

        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')

        fecha_inicio = parse_date(fecha_inicio_str) if isinstance(fecha_inicio_str, str) else None
        fecha_fin = parse_date(fecha_fin_str) if isinstance(fecha_fin_str, str) else None

        ventas = Venta.objects.all()
        compras = Compra.objects.all()

        if cliente_id:
            ventas = ventas.filter(cliente_id=cliente_id)
        if proveedor_id:
            compras = compras.filter(proveedor_id=proveedor_id)

        if fecha_inicio and fecha_fin:
            ventas = ventas.filter(fecha__range=[fecha_inicio, fecha_fin])
            compras = compras.filter(fecha__range=[fecha_inicio, fecha_fin])

        total_ventas = ventas.aggregate(total=Sum('total'))['total'] or 0
        total_compras = compras.aggregate(total=Sum('total'))['total'] or 0
        rentabilidad = total_ventas - total_compras

        return Response({
            "ventas": total_ventas,
            "compras": total_compras,
            "rentabilidad": rentabilidad,
        })



class CicloConversionEfectivoView(APIView):
    def get(self, request):
        empresa_id = request.query_params.get('empresa')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        ventas = Venta.objects.all()
        compras = Compra.objects.all()

        if empresa_id:
            ventas = ventas.filter(empresa_id=empresa_id)
            compras = compras.filter(empresa_id=empresa_id)

        if fecha_inicio and fecha_fin:
            ventas = ventas.filter(fecha__range=[fecha_inicio, fecha_fin])
            compras = compras.filter(fecha__range=[fecha_inicio, fecha_fin])

        cxc_qs = CuentaPorCobrar.objects.filter(venta__in=ventas)
        cxc_qs = cxc_qs.annotate(
            dias_para_cobro=ExpressionWrapper(
                F('fecha_vencimiento') - F('venta__fecha'),
                output_field=DurationField()
            )
        )

        cxc_avg = cxc_qs.aggregate(avg=Avg('dias_para_cobro'))['avg']

        if cxc_avg:
            promedio_dias_cobro = cxc_avg.total_seconds() / (60*60*24)
        else:
            promedio_dias_cobro = 0

        cxp_qs = CuentaPorPagar.objects.filter(compra__in=compras)
        cxp_qs = cxp_qs.annotate(
            dias_para_pago=ExpressionWrapper(
                F('fecha_vencimiento') - F('compra__fecha'),
                output_field=DurationField()
            )
        )

        cxp_avg = cxp_qs.aggregate(avg=Avg('dias_para_pago'))['avg']

        if cxp_avg:
            promedio_dias_pago = cxp_avg.total_seconds() / (60*60*24)
        else:
            promedio_dias_pago = 0

        ciclo = round(promedio_dias_cobro - promedio_dias_pago, 2)

        return Response({"ciclo_conversion_efectivo": ciclo})



class LiquidezCorrienteView(APIView):
    """
    Vista para obtener el ratio de liquidez corriente con filtros por fecha, empresa y sucursal.
    """
    def get(self, request):
        empresa_id = request.query_params.get('empresa')
        fecha_inicio = parse_date(request.query_params.get('fecha_inicio'))
        fecha_fin = parse_date(request.query_params.get('fecha_fin'))

        cxc = CuentaPorCobrar.objects.filter(estado='PENDIENTE')
        cxp = CuentaPorPagar.objects.filter(estado='PENDIENTE')

        if empresa_id:
            cxc = cxc.filter(venta__empresa_id=empresa_id)
            cxp = cxp.filter(compra__empresa_id=empresa_id)

        if fecha_inicio and fecha_fin:
            cxc = cxc.filter(fecha_vencimiento__range=[fecha_inicio, fecha_fin])
            cxp = cxp.filter(fecha_vencimiento__range=[fecha_inicio, fecha_fin])

        activos_corrientes = cxc.aggregate(total=Sum('monto'))['total'] or 0
        pasivos_corrientes = cxp.aggregate(total=Sum('monto'))['total'] or 0

        if pasivos_corrientes == 0:
            ratio = "N/A"
        else:
            ratio = round(activos_corrientes / pasivos_corrientes, 2)

        return Response({"liquidez_corriente": ratio})



# --- /home/runner/workspace/finanzas/views/pagos.py ---
from finanzas.models import Pago
from finanzas.serializers import PagoSerializer
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from contabilidad.utils.asientos import registrar_asiento_pago
from rest_framework.exceptions import ValidationError
from contabilidad.models import AsientoContable

class PagoViewSet(viewsets.ModelViewSet):
    # ...
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer  # ✅ <-- esta línea es obligatoria
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pago = serializer.save()

        # Crear asiento contable automático
        try:
            registrar_asiento_pago(pago, request.user)
        except Exception as e:
            # Loguear error en consola (puedes usar logging)
            print(f"Error al registrar asiento contable: {e}")
            # Retornar respuesta exitosa pero con advertencia
            return Response({
                "pago": PagoSerializer(pago).data,
                "advertencia": f"No se pudo registrar el asiento contable: {str(e)}"
            }, status=status.HTTP_201_CREATED)

        return Response(PagoSerializer(pago).data, status=status.HTTP_201_CREATED)


    def destroy(self, request, *args, **kwargs):
        pago = self.get_object()

        asiento = AsientoContable.objects.filter(
            referencia_id=pago.id,
            referencia_tipo='Pago',
            empresa=pago.empresa
        ).first()

        if asiento and asiento.conciliado:
            raise ValidationError("No se puede eliminar este pago porque su asiento contable ya está conciliado o cerrado.")

        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        pago = self.get_object()
        asiento = AsientoContable.objects.filter(
            referencia_id=pago.id,
            referencia_tipo='Pago',
            empresa=pago.empresa
        ).first()

        if asiento and asiento.conciliado:
            return Response(
                {"detail": "No se puede modificar este pago porque su asiento contable ya está conciliado o cerrado."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)




# --- /home/runner/workspace/finanzas/serializers/__init__.py ---
from .cuentas_por_cobrar_serializer import CuentaPorCobrarSerializer
from .cuentas_por_pagar_serializer import CuentaPorPagarSerializer
from .pago_serializer import PagoSerializer



# --- /home/runner/workspace/finanzas/serializers/cuentas_por_cobrar_serializer.py ---
from finanzas.models import CuentaPorCobrar
from rest_framework import serializers

class CuentaPorCobrarSerializer(serializers.ModelSerializer):
    venta = serializers.PrimaryKeyRelatedField(read_only=True)
    monto_pagado = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    saldo = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = CuentaPorCobrar
        fields = [
            'id',
            'venta',
            'monto',
            'monto_pagado',
            'saldo',
            'fecha_vencimiento',
            'estado',
            'notas',
        ]
        read_only_fields = ['id', 'monto_pagado', 'saldo', 'estado']



# --- /home/runner/workspace/finanzas/serializers/cuentas_por_pagar_serializer.py ---
from rest_framework import serializers
from finanzas.models import CuentaPorPagar, Pago

class CuentaPorPagarSerializer(serializers.ModelSerializer):
    compra = serializers.PrimaryKeyRelatedField(read_only=True)
    monto_pagado = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    saldo = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = CuentaPorPagar
        fields = [
            'id',
            'compra',
            'monto',
            'monto_pagado',
            'saldo',
            'fecha_vencimiento',
            'estado',
            'notas',
        ]
        read_only_fields = ['id', 'monto_pagado', 'saldo', 'estado']



# --- /home/runner/workspace/finanzas/serializers/pago_serializer.py ---
from finanzas.models import Pago, CuentaPorPagar, CuentaPorCobrar
from rest_framework import serializers
from django.core.exceptions import ValidationError

class PagoSerializer(serializers.ModelSerializer):
    cuenta_pagar = serializers.PrimaryKeyRelatedField(
        queryset=CuentaPorPagar.objects.all(), allow_null=True, required=False
    )
    cuenta_cobrar = serializers.PrimaryKeyRelatedField(
        queryset=CuentaPorCobrar.objects.all(), allow_null=True, required=False
    )
    saldo_actual = serializers.SerializerMethodField(read_only=True)
    tipo_cuenta = serializers.SerializerMethodField(read_only=True)
    comprobante = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Pago
        fields = [
            'id',
            'cuenta_pagar',
            'cuenta_cobrar',
            'monto',
            'fecha',
            'metodo_pago',
            'saldo_actual',
            'tipo_cuenta',
            'observaciones',
            'comprobante',
        ]
        read_only_fields = ['id', 'saldo_actual', 'tipo_cuenta']

    def get_saldo_actual(self, obj):
        if obj.cuenta_pagar:
            return obj.cuenta_pagar.saldo_pendiente
        if obj.cuenta_cobrar:
            return obj.cuenta_cobrar.saldo_pendiente
        return None

    def get_tipo_cuenta(self, obj):
        if obj.cuenta_pagar:
            return 'CuentaPorPagar'
        if obj.cuenta_cobrar:
            return 'CuentaPorCobrar'
        return None

    def validate(self, data):
        cuenta_pagar = data.get('cuenta_pagar')
        cuenta_cobrar = data.get('cuenta_cobrar')
        monto = data.get('monto')

        if not cuenta_pagar and not cuenta_cobrar:
            raise serializers.ValidationError("El pago debe estar vinculado a una cuenta por pagar o por cobrar.")
        if cuenta_pagar and cuenta_cobrar:
            raise serializers.ValidationError("El pago no puede estar vinculado a ambas cuentas a la vez.")

        # Obtener saldo pendiente para validar monto
        saldo_pendiente = None
        if cuenta_pagar:
            saldo_pendiente = cuenta_pagar.saldo_pendiente
        elif cuenta_cobrar:
            saldo_pendiente = cuenta_cobrar.saldo_pendiente

        if monto is None or monto <= 0:
            raise serializers.ValidationError("El monto del pago debe ser mayor a cero.")
        if saldo_pendiente is not None and monto > saldo_pendiente:
            raise serializers.ValidationError(f"El monto del pago (${monto}) no puede exceder el saldo pendiente (${saldo_pendiente}).")

        return data



# --- /home/runner/workspace/finanzas/tests/__init__.py ---



# --- /home/runner/workspace/finanzas/tests/test_finanzas.py ---

from django.core.exceptions import ValidationError

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from accounts.models import Usuario
from core.models import Empresa
from compras.models import Proveedor, Compra
from ventas.models import Venta, Cliente
from finanzas.models import CuentaPorCobrar, CuentaPorPagar, Pago, MetodoPagoChoices
from decimal import Decimal

class FinanzasTests(TestCase):
    def setUp(self):
        # Crear una empresa sin especificar el ID (se asignará automáticamente)
        self.empresa = Empresa.objects.create(
            nombre="Mi Empresa",
            razon_social="Razón Social",
            rfc="ABC1234567890",
            domicilio_fiscal="Calle Ficticia 123",
            regimen_fiscal="General"
        )

        self.fecha_venc = timezone.now().date() + timedelta(days=7)

        # Crear un usuario de prueba usando el modelo 'Usuario' personalizado
        self.usuario = Usuario.objects.create_user(
            username='testuser', 
            password='testpassword', 
            empresa=self.empresa
        )

        # Crear un proveedor antes de la compra
        self.proveedor = Proveedor.objects.create(
            nombre="Proveedor de prueba",
            empresa=self.empresa
        )

        # Crear un cliente antes de la venta (soluciona el problema de clave foránea)
        self.cliente = Cliente.objects.create(
            nombre="Cliente de prueba",
            empresa=self.empresa
        )


        # Simulamos venta y compra con el usuario asignado
        self.venta = Venta.objects.create(cliente_id=self.cliente.id, total=1000, empresa=self.empresa, usuario=self.usuario)
        self.compra = Compra.objects.create(proveedor=self.proveedor, total=500, empresa=self.empresa)

        # Cuentas
        self.cxc = CuentaPorCobrar.objects.create(
            empresa=self.empresa, venta=self.venta, monto=1000, fecha_vencimiento=self.fecha_venc
        )
        self.cxp = CuentaPorPagar.objects.create(
            empresa=self.empresa, compra=self.compra, monto=500, fecha_vencimiento=self.fecha_venc
        )

    def test_crear_cuenta_por_pagar(self):
        self.assertEqual(self.cxp.monto, Decimal('500.00'))
        self.assertEqual(self.cxp.estado, "PENDIENTE")

    def test_crear_cuenta_por_cobrar(self):
        self.assertEqual(self.cxc.monto, Decimal('1000.00'))
        self.assertEqual(self.cxc.estado, "PENDIENTE")

    def test_pago_parcial_cuenta_por_cobrar(self):
        Pago.objects.create(cuenta_cobrar=self.cxc, monto=400, fecha=timezone.now(), metodo_pago=MetodoPagoChoices.EFECTIVO, empresa=self.empresa)
        self.cxc.refresh_from_db()
        self.assertEqual(self.cxc.estado, "PENDIENTE")
        self.assertEqual(self.cxc.saldo_pendiente, Decimal('600.00'))

    def test_pago_total_cuenta_por_pagar(self):
        Pago.objects.create(cuenta_pagar=self.cxp, monto=500, fecha=timezone.now(), metodo_pago=MetodoPagoChoices.TRANSFERENCIA, empresa=self.empresa)
        self.cxp.refresh_from_db()
        self.assertEqual(self.cxp.estado, "PAGADO")
        self.assertEqual(self.cxp.saldo_pendiente, Decimal('0.00'))


    def test_pago_excesivo_lanza_error(self):
        # Intentamos crear un pago cuyo monto excede el saldo pendiente
        with self.assertRaises(ValidationError):  # Aseguramos que se lance una ValidationError
            pago = Pago.objects.create(
                cuenta_pagar=self.cxp,
                monto=600,
                fecha=timezone.now(),
                metodo_pago=MetodoPagoChoices.CHEQUE,
                empresa=self.empresa
            )
            pago.full_clean()  # Esto ejecuta la validación manualmente antes de guardar



