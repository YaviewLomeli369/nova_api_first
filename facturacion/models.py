from django.db import models
from core.models import Empresa
from ventas.models import Venta
from accounts.models import Usuario

class ComprobanteFiscal(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('TIMBRADO', 'Timbrado'),
        ('CANCELADO', 'Cancelado'),
        ('ERROR', 'Error'),
    ]

    TIPOS_COMPROBANTE = [
        ('FACTURA', 'Factura'),
        ('NOTA_CREDITO', 'Nota de Crédito'),
        ('RECIBO_NOMINA', 'Recibo de Nómina'),
        # Otros tipos CFDI
    ]
  


    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=36, unique=True, blank=True, null=True)  # UUID timbrado
    # xml = models.TextField(blank=True, null=True)  # XML CFDI completo
    xml = models.FileField(upload_to="cfdi_xmls/", null=True, blank=True)
    pdf = models.FileField(upload_to='cfdi_pdfs/', blank=True, null=True)  # PDF factura
    fecha_timbrado = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')  
    error_mensaje = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_COMPROBANTE, default='FACTURA')
    serie = models.CharField(max_length=10, blank=True, null=True)
    folio = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def esta_timbrado(self):
        return self.estado == 'TIMBRADO' and self.uuid is not None

    class Meta:
      indexes = [
          models.Index(fields=['estado']),
          models.Index(fields=['tipo']),
      ]

  
    def __str__(self):
      venta_id = self.venta.id if self.venta else 'N/A'
      return f"{self.get_tipo_display()} {self.uuid or 'Sin UUID'} - Venta {venta_id}"
