# reportes/models.py

from django.db import models
from django.contrib.auth import get_user_model


class ReporteGenerado(models.Model):
    TIPO_REPORTE_CHOICES = [
        ('VENTAS', 'Ventas'),
        ('COMPRAS', 'Compras'),
        ('INVENTARIO', 'Inventario'),
        ('FLUJO_CAJA', 'Flujo de Caja'),
        ('KPI', 'Indicador'),
        ('DASHBOARD', 'Dashboard'),
        ('OTRO', 'Otro'),
    ]

    ESTADO_REPORTE_CHOICES = [
        ('GENERANDO', 'Generando'),
        ('COMPLETO', 'Completo'),
        ('FALLIDO', 'Fallido'),
    ]

    nombre = models.CharField(max_length=255, help_text="Nombre amigable del reporte.")
    tipo = models.CharField(max_length=50, choices=TIPO_REPORTE_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_REPORTE_CHOICES, default='GENERANDO')

    filtros_usados = models.JSONField(help_text="Filtros aplicados al generar el reporte (fecha, usuario, etc.)")

    archivo_pdf = models.FileField(upload_to='reportes/pdf/', null=True, blank=True)
    archivo_excel = models.FileField(upload_to='reportes/excel/', null=True, blank=True)
    archivo_csv = models.FileField(upload_to='reportes/csv/', null=True, blank=True)

    generado_por = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    empresa = models.ForeignKey('core.Empresa', on_delete=models.CASCADE)

    generado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-generado_en']
        verbose_name = "Reporte Generado"
        verbose_name_plural = "Reportes Generados"

    def __str__(self):
        return f"{self.nombre} ({self.tipo}) - {self.estado}"

    @property
    def esta_completo(self):
        return self.estado == 'COMPLETO'

    @property
    def url_descarga_pdf(self):
        return self.archivo_pdf.url if self.archivo_pdf else None

    @property
    def url_descarga_excel(self):
        return self.archivo_excel.url if self.archivo_excel else None

    @property
    def url_descarga_csv(self):
        return self.archivo_csv.url if self.archivo_csv else None
