from django.db import models
from core.models import Empresa
from ventas.models import Venta
from accounts.models import Usuario
from django.core.exceptions import ValidationError

class MetodoPagoChoices(models.TextChoices):
    PUE = 'PUE', 'Pago en una sola exhibición'
    PPD = 'PPD', 'Pago en parcialidades o diferido'

# Fuente oficial: Catálogo SAT c_FormaPago vigente al 2025
# https://www.sat.gob.mx/consultas/42930/catalogo-de-forma-de-pago
class FormaPagoChoices(models.TextChoices):
    EFECTIVO = '01', 'Efectivo'
    CHEQUE_NOMINATIVO = '02', 'Cheque nominativo'
    TRANSFERENCIA_ELECTRONICA = '03', 'Transferencia electrónica de fondos'
    TARJETA_CREDITO = '04', 'Tarjeta de crédito'
    MONEDERO_ELECTRONICO = '05', 'Monedero electrónico'
    DINERO_ELECTRONICO = '06', 'Dinero electrónico'
    VALES_DESPENSA = '08', 'Vales de despensa'
    DACION_EN_PAGO = '12', 'Dación en pago'
    PAGO_SUBROGACION = '13', 'Pago por subrogación'
    PAGO_CONSIGNACION = '14', 'Pago por consignación'
    CONDONACION = '15', 'Condonación'
    COMPENSACION = '17', 'Compensación'
    NOVACION = '23', 'Novación'
    CONFUSION = '24', 'Confusión'
    REMISION_DE_DEUDA = '25', 'Remisión de deuda'
    PRESCRIPCION_CADUCIDAD = '26', 'Prescripción o caducidad'
    SATISFACCION_ACREEDOR = '27', 'A satisfacción del acreedor'
    TARJETA_DEBITO = '28', 'Tarjeta de débito'
    TARJETA_SERVICIOS = '29', 'Tarjeta de servicios'
    APLICACION_ANTICIPOS = '30', 'Aplicación de anticipos'
    INTERMEDIARIO_PAGOS = '31', 'Intermediario de pagos'
    POR_DEFINIR = '99', 'Por definir'


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
    metodo_pago = models.CharField(
        max_length=3,
        choices=MetodoPagoChoices.choices,
        blank=True,
        null=True,
        help_text="Método de pago según catálogo SAT (PUE, PPD)"
    )
    forma_pago = models.CharField(
        max_length=3,
        choices=FormaPagoChoices.choices,
        blank=True,
        null=True,
        help_text="Forma de pago clave SAT (Ej: 01 Efectivo, 03 Transferencia)"
    )
    exportacion = models.CharField(
        max_length=2, 
        default='01', 
        choices=[
            ('01', 'No aplica'),
            ('02', 'Definitiva'),
            ('03', 'Temporal'),
        ],
        help_text="Exportación según el catálogo SAT c_Exportacion"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def esta_timbrado(self):
        return self.estado == 'TIMBRADO' and self.uuid is not None

    def clean(self):
        if self.estado == 'TIMBRADO':
            if not self.metodo_pago:
                raise ValidationError({'metodo_pago': "Requerido al estar timbrado."})
            if not self.forma_pago:
                raise ValidationError({'forma_pago': "Requerido al estar timbrado."})
            if not self.empresa or not self.empresa.rfc:
                raise ValidationError({'empresa': "La empresa debe tener RFC."})
            if not self.venta.cliente.rfc:
                raise ValidationError({'venta': "El cliente debe tener RFC para timbrar."})

    class Meta:
      indexes = [
          models.Index(fields=['estado']),
          models.Index(fields=['tipo']),
      ]

  
    def __str__(self):
      venta_id = self.venta.id if self.venta else 'N/A'
      return f"{self.get_tipo_display()} {self.uuid or 'Sin UUID'} - Venta {venta_id}"
