# ventas/models.py (completado)

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Cliente(models.Model):
    empresa = models.ForeignKey('core.Empresa', on_delete=models.CASCADE, related_name='clientes')
    nombre = models.CharField(max_length=200)
    rfc = models.CharField(max_length=13, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['empresa', 'nombre']),
        ]

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

    def calcular_total(self):
        # Sumar los subtotales de los detalles de la venta
        self.total = sum(detalle.precio_unitario * detalle.cantidad for detalle in self.detalles.all())

    def save(self, *args, **kwargs):
        # Asegurarse de que el total se calcule antes de guardar
        self.calcular_total()
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

