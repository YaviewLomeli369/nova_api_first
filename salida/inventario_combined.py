
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


