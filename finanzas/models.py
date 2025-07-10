# finanzas/models.py
from .constants import ESTADO_CUENTA_CHOICES
from django.db import models
from django.utils import timezone
from ventas.models import Venta
from compras.models import Compra
from django.core.exceptions import ValidationError
from django.utils import timezone

class CuentaPorCobrar(models.Model):
    ESTADO_CHOICES = ESTADO_CUENTA_CHOICES

    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='cuentas_por_cobrar')
    monto = models.DecimalField(max_digits=14, decimal_places=2)
    fecha_vencimiento = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')

    def clean(self):
        if self.monto <= 0:
            raise ValidationError("El monto debe ser mayor a cero.")
        if self.fecha_vencimiento < timezone.now().date():
            raise ValidationError("La fecha de vencimiento no puede estar en el pasado.")


    class Meta:
        verbose_name = "Cuenta por Cobrar"
        verbose_name_plural = "Cuentas por Cobrar"
        ordering = ['fecha_vencimiento']
        indexes = [
            models.Index(fields=['fecha_vencimiento', 'estado']),
            models.Index(fields=['venta']),
        ]

    def __str__(self):
        return f"CxC Venta {self.venta.id} - {self.estado} - ${self.monto}"


class CuentaPorPagar(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('VENCIDO', 'Vencido'),
    ]

    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='cuentas_por_pagar')
    monto = models.DecimalField(max_digits=14, decimal_places=2)
    fecha_vencimiento = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')

    def clean(self):
        if self.monto <= 0:
            raise ValidationError("El monto debe ser mayor a cero.")
        if self.fecha_vencimiento < timezone.now().date():
            raise ValidationError("La fecha de vencimiento no puede estar en el pasado.")

    class Meta:
        verbose_name = "Cuenta por Pagar"
        verbose_name_plural = "Cuentas por Pagar"
        ordering = ['fecha_vencimiento']
        indexes = [
            models.Index(fields=['fecha_vencimiento', 'estado']),
            models.Index(fields=['compra']),
        ]

    def __str__(self):
        return f"CxP Compra {self.compra.id} - {self.estado} - ${self.monto}"


class Pago(models.Model):
    METODO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('CHEQUE', 'Cheque'),
        ('OTRO', 'Otro'),
    ]

    cuenta_cobrar = models.ForeignKey(CuentaPorCobrar, on_delete=models.CASCADE, null=True, blank=True, related_name='pagos')
    cuenta_pagar = models.ForeignKey(CuentaPorPagar, on_delete=models.CASCADE, null=True, blank=True, related_name='pagos')
    monto = models.DecimalField(max_digits=14, decimal_places=2)
    fecha = models.DateField(default=timezone.now)
    metodo_pago = models.CharField(max_length=50)

    def clean(self):
        if self.monto <= 0:
            raise ValidationError("El monto del pago debe ser positivo.")
        if not self.cuenta_cobrar and not self.cuenta_pagar:
            raise ValidationError("El pago debe estar vinculado a una cuenta por pagar o por cobrar.")

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['metodo_pago']),
        ]

    def __str__(self):
        cuenta = 'CxC' if self.cuenta_cobrar else 'CxP' if self.cuenta_pagar else 'N/A'
        referencia_id = self.cuenta_cobrar.id if self.cuenta_cobrar else self.cuenta_pagar.id if self.cuenta_pagar else 'N/A'
        return f"Pago {cuenta} ID {referencia_id} - ${self.monto} - {self.fecha}"
