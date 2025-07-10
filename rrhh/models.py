# rrhh/models.py

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Empleado(models.Model):
    empresa = models.ForeignKey('core.Empresa', on_delete=models.CASCADE, related_name='empleados')
    nombre = models.CharField(max_length=200)
    rfc = models.CharField(max_length=13, blank=True, null=True)
    puesto = models.CharField(max_length=100)
    salario = models.DecimalField(max_digits=14, decimal_places=2)

    def clean(self):
        if self.salario < 0:
            raise ValidationError("El salario no puede ser negativo.")


    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['empresa', 'nombre']),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.puesto}"


class Nomina(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADA', 'Pagada'),
        ('CANCELADA', 'Cancelada'),
    ]

    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='nominas')
    periodo = models.CharField(max_length=50, help_text="Ejemplo: 'Julio 2025'")
    total = models.DecimalField(max_digits=14, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')

    class Meta:
        verbose_name = "Nómina"
        verbose_name_plural = "Nóminas"
        ordering = ['-periodo']
        indexes = [
            models.Index(fields=['empleado', 'periodo']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f"Nómina {self.periodo} - {self.empleado.nombre} - {self.estado}"


class Asistencia(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()

    class Meta:
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['empleado', 'fecha']),
        ]

    def __str__(self):
        return f"Asistencia {self.empleado.nombre} - {self.fecha}"
