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

