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
