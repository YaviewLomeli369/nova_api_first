# ventas/models.py (completado)

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Cliente(models.Model):
    empresa = models.ForeignKey('core.Empresa', on_delete=models.CASCADE, related_name='clientes')
    nombre = models.CharField(max_length=200)
    apellido_paterno = models.CharField(max_length=100, blank=True, null=True)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    rfc = models.CharField(max_length=13, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    uso_cfdi = models.CharField(max_length=3, blank=True, null=True, help_text="Uso CFDI SAT (G03, S01, etc.)")
    regimen_fiscal = models.CharField(max_length=3, blank=True, null=True, help_text="Régimen fiscal del receptor")

    direccion_calle = models.CharField(max_length=150, blank=True, null=True)
    direccion_num_ext = models.CharField(max_length=10, blank=True, null=True)
    direccion_num_int = models.CharField(max_length=10, blank=True, null=True)
    direccion_colonia = models.CharField(max_length=100, blank=True, null=True)
    direccion_municipio = models.CharField(max_length=100, blank=True, null=True)
    direccion_estado = models.CharField(max_length=100, blank=True, null=True)
    direccion_pais = models.CharField(max_length=50, default='MEX')
    direccion_codigo_postal = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['empresa', 'nombre']),
        ]

    @property
    def nombre_completo(self):
        apellidos = ' '.join(filter(None, [self.apellido_paterno, self.apellido_materno]))
        return f"{self.nombre} {apellidos}".strip()

    def clean(self):
        if self.rfc and self.uso_cfdi == "P01" and self.rfc != "XAXX010101000":
            raise ValidationError("El uso CFDI 'P01' solo es válido con RFC genérico.")

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]

    empresa = models.ForeignKey('core.Empresa', on_delete=models.CASCADE, related_name='ventas')
    sucursal = models.ForeignKey('core.Sucursal', on_delete=models.PROTECT, related_name='ventas')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas')
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=14, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')
    usuario = models.ForeignKey('accounts.Usuario', on_delete=models.PROTECT, related_name='ventas')
    condiciones_pago = models.CharField(max_length=100, blank=True, null=True, help_text="Ej: Contado, Crédito 30 días")
    moneda = models.CharField(max_length=5, blank=True, null=True, default="MXN", help_text="Ej: MXN, USD")

    FORMA_PAGO_CHOICES = [
        ('01', 'Efectivo'),
        ('02', 'Cheque nominativo'),
        ('03', 'Transferencia electrónica de fondos'),
        ('04', 'Tarjeta de crédito'),
        ('05', 'Monedero electrónico'),
        ('06', 'Dinero electrónico'),
        ('08', 'Vales de despensa'),
        ('12', 'Dación en pago'),
        ('13', 'Pago por subrogación'),
        ('14', 'Pago por consignación'),
        ('15', 'Condonación'),
        ('17', 'Compensación'),
        ('23', 'Novación'),
        ('24', 'Confusión'),
        ('25', 'Remisión de deuda'),
        ('26', 'Prescripción o caducidad'),
        ('27', 'A satisfacción del acreedor'),
        ('28', 'Tarjeta de débito'),
        ('29', 'Tarjeta de servicios'),
        ('30', 'Aplicación de anticipos'),
        ('31', 'Intermediario pagos'),
        ('99', 'Por definir'),
    ]

    METODO_PAGO_CHOICES = [
        ('PUE', 'Pago en una sola exhibición'),
        ('PPD', 'Pago en parcialidades o diferido'),
    ]

    forma_pago = models.CharField(
        max_length=2,
        choices=FORMA_PAGO_CHOICES,
        default='01'
    )

    metodo_pago = models.CharField(
        max_length=3,
        choices=METODO_PAGO_CHOICES,
        default='PUE'
    )

    def calcular_total(self):
        # Solo calcular si ya tenemos un ID (la venta ya fue guardada)
        if self.pk:
            self.total = sum(detalle.precio_unitario * detalle.cantidad for detalle in self.detalles.all())
        else:
            # Si no tiene ID, establecer total en 0 inicialmente
            self.total = 0

    def save(self, *args, **kwargs):
        if not self.pk:
            self.total = 0
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

    @property
    def importe(self):
        return Decimal(self.precio_unitario) * Decimal(self.cantidad)


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

@receiver([post_save, post_delete], sender=DetalleVenta)
def actualizar_total_venta(sender, instance, **kwargs):
    venta = instance.venta
    total = venta.detalles.aggregate(
        total=models.Sum(models.F('precio_unitario') * models.F('cantidad'))
    )['total'] or 0
    venta.total = total
    venta.save(update_fields=['total'])