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


class Compra(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='compras')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='compras')
    fecha = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=14, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='compras_creadas')

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

    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a cero.")
        if self.precio_unitario <= 0:
            raise ValidationError("El precio unitario debe ser mayor a cero.")


    class Meta:
        verbose_name = "Detalle de Compra"
        verbose_name_plural = "Detalles de Compras"
        unique_together = ('compra', 'producto')

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad} x {self.precio_unitario}'

