
# --- /home/runner/workspace/finanzas/__init__.py ---



# --- /home/runner/workspace/finanzas/admin.py ---
from django.contrib import admin

# Register your models here.



# --- /home/runner/workspace/finanzas/apps.py ---
from django.apps import AppConfig


class FinanzasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finanzas'



# --- /home/runner/workspace/finanzas/tests.py ---
from django.test import TestCase

# Create your tests here.



# --- /home/runner/workspace/finanzas/constants.py ---
# finanzas/constants.py (nuevo archivo)
ESTADO_CUENTA_CHOICES = [
    ('PENDIENTE', 'Pendiente'),
    ('PAGADO', 'Pagado'),
    ('VENCIDO', 'Vencido'),
]


# --- /home/runner/workspace/finanzas/urls.py ---
from rest_framework.routers import DefaultRouter
from finanzas.views.cuentas_por_cobrar import  CuentaPorCobrarViewSet 
from finanzas.views.cuentas_por_pagar import CuentaPorPagarViewSet
from finanzas.views.pagos import  PagoViewSet


router = DefaultRouter()
router.register(r'cuentas_por_pagar', CuentaPorPagarViewSet, basename='cuentas_por_pagar')
router.register(r'cuentas_por_cobrar', CuentaPorCobrarViewSet, basename='cuentas_por_cobrar')
router.register(r'pagos', PagoViewSet, basename='pagos')

urlpatterns = router.urls


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

    def clean(self):
        if self.monto <= 0:
            raise ValidationError("El monto del pago debe ser mayor a cero.")
        if not self.cuenta_cobrar and not self.cuenta_pagar:
            raise ValidationError("El pago debe estar vinculado a una cuenta por cobrar o por pagar.")
        if self.cuenta_cobrar and self.cuenta_pagar:
            raise ValidationError("Un pago no puede estar vinculado a ambas cuentas a la vez.")

    def save(self, *args, **kwargs):
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

# # finanzas/models.py
# from .constants import ESTADO_CUENTA_CHOICES
# from django.db import models
# from django.utils import timezone
# from ventas.models import Venta
# from compras.models import Compra
# from django.core.exceptions import ValidationError
# from django.utils import timezone

# class CuentaPorCobrar(models.Model):
#     ESTADO_CHOICES = ESTADO_CUENTA_CHOICES

#     venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='cuentas_por_cobrar')
#     monto = models.DecimalField(max_digits=14, decimal_places=2)
#     fecha_vencimiento = models.DateField()
#     estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')

#     def clean(self):
#         if self.monto <= 0:
#             raise ValidationError("El monto debe ser mayor a cero.")
#         if self.fecha_vencimiento < timezone.now().date():
#             raise ValidationError("La fecha de vencimiento no puede estar en el pasado.")


#     class Meta:
#         verbose_name = "Cuenta por Cobrar"
#         verbose_name_plural = "Cuentas por Cobrar"
#         ordering = ['fecha_vencimiento']
#         indexes = [
#             models.Index(fields=['fecha_vencimiento', 'estado']),
#             models.Index(fields=['venta']),
#         ]

#     def __str__(self):
#         return f"CxC Venta {self.venta.id} - {self.estado} - ${self.monto}"


# class CuentaPorPagar(models.Model):
#     ESTADO_CHOICES = [
#         ('PENDIENTE', 'Pendiente'),
#         ('PAGADO', 'Pagado'),
#         ('VENCIDO', 'Vencido'),
#     ]

#     compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='cuentas_por_pagar')
#     monto = models.DecimalField(max_digits=14, decimal_places=2)
#     fecha_vencimiento = models.DateField()
#     estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')

#     def clean(self):
#         if self.monto <= 0:
#             raise ValidationError("El monto debe ser mayor a cero.")
#         if self.fecha_vencimiento < timezone.now().date():
#             raise ValidationError("La fecha de vencimiento no puede estar en el pasado.")

#     class Meta:
#         verbose_name = "Cuenta por Pagar"
#         verbose_name_plural = "Cuentas por Pagar"
#         ordering = ['fecha_vencimiento']
#         indexes = [
#             models.Index(fields=['fecha_vencimiento', 'estado']),
#             models.Index(fields=['compra']),
#         ]

#     def __str__(self):
#         return f"CxP Compra {self.compra.id} - {self.estado} - ${self.monto}"


# class Pago(models.Model):
#     METODO_PAGO_CHOICES = [
#         ('EFECTIVO', 'Efectivo'),
#         ('TARJETA', 'Tarjeta'),
#         ('TRANSFERENCIA', 'Transferencia'),
#         ('CHEQUE', 'Cheque'),
#         ('OTRO', 'Otro'),
#     ]

#     cuenta_cobrar = models.ForeignKey(CuentaPorCobrar, on_delete=models.CASCADE, null=True, blank=True, related_name='pagos')
#     cuenta_pagar = models.ForeignKey(CuentaPorPagar, on_delete=models.CASCADE, null=True, blank=True, related_name='pagos')
#     monto = models.DecimalField(max_digits=14, decimal_places=2)
#     fecha = models.DateField(default=timezone.now)
#     metodo_pago = models.CharField(max_length=50)

#     def clean(self):
#         if self.monto <= 0:
#             raise ValidationError("El monto del pago debe ser positivo.")
#         if not self.cuenta_cobrar and not self.cuenta_pagar:
#             raise ValidationError("El pago debe estar vinculado a una cuenta por pagar o por cobrar.")

#     class Meta:
#         verbose_name = "Pago"
#         verbose_name_plural = "Pagos"
#         ordering = ['-fecha']
#         indexes = [
#             models.Index(fields=['fecha']),
#             models.Index(fields=['metodo_pago']),
#         ]

#     def __str__(self):
#         cuenta = 'CxC' if self.cuenta_cobrar else 'CxP' if self.cuenta_pagar else 'N/A'
#         referencia_id = self.cuenta_cobrar.id if self.cuenta_cobrar else self.cuenta_pagar.id if self.cuenta_pagar else 'N/A'
#         return f"Pago {cuenta} ID {referencia_id} - ${self.monto} - {self.fecha}"



# --- /home/runner/workspace/finanzas/migrations/__init__.py ---



# --- /home/runner/workspace/finanzas/migrations/0001_initial.py ---
# Generated by Django 5.2.4 on 2025-07-04 22:50

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('compras', '0001_initial'),
        ('ventas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CuentaPorCobrar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=14)),
                ('fecha_vencimiento', models.DateField()),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('PAGADO', 'Pagado'), ('VENCIDO', 'Vencido')], default='PENDIENTE', max_length=10)),
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
                ('compra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cuentas_por_pagar', to='compras.compra')),
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
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('metodo_pago', models.CharField(max_length=50)),
                ('cuenta_cobrar', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='finanzas.cuentaporcobrar')),
                ('cuenta_pagar', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='finanzas.cuentaporpagar')),
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



# --- /home/runner/workspace/finanzas/migrations/0002_cuentaporcobrar_empresa_cuentaporpagar_empresa_and_more.py ---
# Generated by Django 5.2.4 on 2025-07-19 04:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('finanzas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cuentaporcobrar',
            name='empresa',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, related_name='cuentas_por_cobrar', to='core.empresa'),
        ),
        migrations.AddField(
            model_name='cuentaporpagar',
            name='empresa',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, related_name='cuentas_por_pagar', to='core.empresa'),
        ),
        migrations.AddField(
            model_name='pago',
            name='empresa',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='core.empresa'),
        ),
        migrations.AlterField(
            model_name='pago',
            name='metodo_pago',
            field=models.CharField(choices=[('EFECTIVO', 'Efectivo'), ('TARJETA', 'Tarjeta'), ('TRANSFERENCIA', 'Transferencia'), ('CHEQUE', 'Cheque'), ('OTRO', 'Otro')], max_length=20),
        ),
    ]



# --- /home/runner/workspace/finanzas/migrations/0003_pago_observaciones.py ---
# Generated by Django 5.2.4 on 2025-07-19 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finanzas', '0002_cuentaporcobrar_empresa_cuentaporpagar_empresa_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pago',
            name='observaciones',
            field=models.TextField(blank=True, null=True),
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



# --- /home/runner/workspace/finanzas/views/pagos.py ---
from finanzas.models import Pago
from finanzas.serializers import PagoSerializer
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class PagoViewSet(viewsets.ModelViewSet):
    """
    Listar todos los pagos y crear pagos nuevos.
    """
    queryset = Pago.objects.select_related('cuenta_cobrar', 'cuenta_pagar').all()
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pago = serializer.save()

        # La lógica para actualizar el estado se encuentra dentro del método save() del serializer

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# --- /home/runner/workspace/finanzas/serializers/__init__.py ---
from .cuentas_por_cobrar_serializer import CuentaPorCobrarSerializer
from .cuentas_por_pagar_serializer import CuentaPorPagarSerializer
from .pago_serializer import PagoSerializer



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
        ]
        read_only_fields = ['id', 'monto_pagado', 'saldo', 'estado']


