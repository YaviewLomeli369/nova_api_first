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

