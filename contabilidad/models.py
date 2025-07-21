from django.db import models
from django.utils import timezone
from accounts.models import Usuario, Empresa
from django.core.exceptions import ValidationError

# ---------------------- MODELO BASE DE CUENTAS ----------------------

class CuentaContable(models.Model):
    """
    Catálogo de cuentas contables según el plan contable de la empresa.
    Puede ser compartido entre empresas o personalizado por empresa.
    """
    CLASIFICACIONES = [
        ('activo', 'Activo'),
        ('pasivo', 'Pasivo'),
        ('patrimonio', 'Patrimonio'),
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
    ]

    codigo = models.CharField(max_length=10, help_text="Código único, ej: 1020")
    nombre = models.CharField(max_length=255, help_text="Ej: Banco BBVA")
    clasificacion = models.CharField(max_length=20, choices=CLASIFICACIONES)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='cuentas_contables')
    es_auxiliar = models.BooleanField(default=True, help_text="Marca si la cuenta es de movimiento o de agrupación")
    padre = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subcuentas')
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cuenta Contable"
        verbose_name_plural = "Cuentas Contables"
        ordering = ['codigo']
        unique_together = ('codigo', 'empresa')

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

# ---------------------- MODELO DE ASIENTOS ----------------------

class AsientoContable(models.Model):
    """
    Representa un asiento contable (doble partida).
    Puede ser generado automáticamente por otros módulos (ej: pagos).
    """
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='asientos_contables')
    fecha = models.DateField(default=timezone.now)
    concepto = models.CharField(max_length=255)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='asientos_creados')
    creado_en = models.DateTimeField(auto_now_add=True)
    conciliado = models.BooleanField(default=False, help_text="Indica si el asiento está conciliado o cerrado")

    # 🔗 Referencia al objeto origen (ej: Pago, Compra, etc.)
    referencia_id = models.PositiveBigIntegerField(null=True, blank=True, help_text="ID del objeto origen (ej: pago, compra, etc.)")
    referencia_tipo = models.CharField(max_length=100, null=True, blank=True, help_text="Tipo de objeto origen (ej: 'Pago', 'Compra')")

    # 🧾 Totales rápidos para reportes
    total_debe = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_haber = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # ⚙️ Indica si fue generado automáticamente
    es_automatico = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Asiento Contable"
        verbose_name_plural = "Asientos Contables"
        ordering = ['-fecha', '-creado_en']
        indexes = [
            models.Index(fields=['empresa', 'fecha']),
            models.Index(fields=['referencia_tipo', 'referencia_id']),
        ]

    def __str__(self):
        return f"Asiento #{self.id} - {self.concepto} ({self.fecha})"

    def actualizar_totales(self):
        """
        Suma todos los debe/haber de sus detalles y actualiza los campos total_debe y total_haber.
        """
        self.total_debe = sum(d.debe for d in self.detalles.all())
        self.total_haber = sum(d.haber for d in self.detalles.all())
        self.save(update_fields=['total_debe', 'total_haber'])

# ---------------------- DETALLES DE ASIENTO ----------------------

class DetalleAsiento(models.Model):
    """
    Detalle de una línea contable (debe o haber).
    Usa una cuenta contable como FK.
    """
    asiento = models.ForeignKey(AsientoContable, on_delete=models.CASCADE, related_name='detalles')
    cuenta_contable = models.ForeignKey(CuentaContable, on_delete=models.PROTECT, related_name='movimientos')
    debe = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    haber = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción opcional para este movimiento.")

    class Meta:
        verbose_name = "Detalle de Asiento"
        verbose_name_plural = "Detalles de Asientos"
        ordering = ['cuenta_contable']
        indexes = [
            models.Index(fields=['asiento', 'cuenta_contable']),
        ]
        constraints = [
            models.CheckConstraint(
                check=~(models.Q(debe=0) & models.Q(haber=0)),
                name='debe_o_haber_no_pueden_ser_cero',
            )
        ]

    def clean(self):
        if self.debe < 0 or self.haber < 0:
            raise ValidationError("Debe y Haber no pueden ser negativos.")
        if self.debe == 0 and self.haber == 0:
            raise ValidationError("Debe o Haber deben tener un valor distinto de cero.")
        if self.debe > 0 and self.haber > 0:
            raise ValidationError("No puede tener valores en ambos campos a la vez.")

    def __str__(self):
        return f"{self.cuenta_contable.codigo} | Debe: {self.debe} | Haber: {self.haber}"
