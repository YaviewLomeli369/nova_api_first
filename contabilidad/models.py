# contabilidad/models.py

from django.db import models
from django.utils import timezone
from accounts.models import Usuario, Empresa
from django.core.exceptions import ValidationError
from django.utils import timezone


class AsientoContable(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='asientos_contables')
    fecha = models.DateField(default=timezone.now)
    concepto = models.CharField(max_length=255)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='asientos_creados')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Asiento Contable"
        verbose_name_plural = "Asientos Contables"
        ordering = ['-fecha', '-creado_en']
        indexes = [
            models.Index(fields=['empresa', 'fecha']),
        ]

    def __str__(self):
        return f"Asiento {self.id} - {self.concepto} ({self.fecha})"


class DetalleAsiento(models.Model):
    asiento = models.ForeignKey(AsientoContable, on_delete=models.CASCADE, related_name='detalles')
    cuenta_contable = models.CharField(max_length=100)  # Ejemplo: "1105 - Caja"
    debe = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    haber = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def clean(self):
        if self.debe < 0 or self.haber < 0:
            raise ValidationError("Debe y Haber no pueden ser negativos.")
        if self.debe == 0 and self.haber == 0:
            raise ValidationError("Debe o Haber deben tener un valor distinto de cero.")


    class Meta:
        verbose_name = "Detalle de Asiento"
        verbose_name_plural = "Detalles de Asientos"
        ordering = ['cuenta_contable']
        indexes = [
            models.Index(fields=['asiento', 'cuenta_contable']),
        ]
        # Opcional: agregar restricción para que debe y haber no sean ambos cero, se haría con CheckConstraint (Django 2.2+)
        constraints = [
            models.CheckConstraint(
                check=~(models.Q(debe=0) & models.Q(haber=0)),
                name='debe_o_haber_no_pueden_ser_cero',
            )
        ]

    def __str__(self):
        return f"{self.cuenta_contable} | Debe: {self.debe} | Haber: {self.haber}"
