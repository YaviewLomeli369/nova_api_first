# documentos/models.py

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


class DocumentoFiscal(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('CFDI', 'CFDI'),
        ('XML', 'XML'),
        ('PDF', 'PDF'),
        ('OTRO', 'Otro'),
    ]

    tipo_documento = models.CharField(
        max_length=10,
        choices=TIPO_DOCUMENTO_CHOICES,
        default='CFDI',
        help_text="Tipo de documento fiscal (CFDI, XML, PDF, etc.)"
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Tipo de modelo referenciado (venta, compra, asiento, etc.)"
    )
    object_id = models.PositiveIntegerField(
        help_text="ID de la entidad relacionada"
    )
    referencia = GenericForeignKey('content_type', 'object_id')

    archivo = models.FileField(
        upload_to='documentos_fiscales/%Y/%m/%d/',
        help_text="Archivo digital del documento (PDF, XML, etc.)"
    )
    fecha_emision = models.DateField(
        default=timezone.now,
        help_text="Fecha de emisión del documento"
    )

    class Meta:
        verbose_name = "Documento Fiscal"
        verbose_name_plural = "Documentos Fiscales"
        indexes = [
            models.Index(fields=['tipo_documento']),
            models.Index(fields=['content_type', 'object_id']),
        ]
        ordering = ['-fecha_emision']

    def __str__(self):
        return f"{self.get_tipo_documento_display()} - Ref: {self.referencia} - {self.fecha_emision}"
