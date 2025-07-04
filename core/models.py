# core/models.py

from django.db import models
from django.utils import timezone


class Empresa(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    rfc = models.CharField(max_length=13, unique=True)  # RFC México: 12 o 13 caracteres
    domicilio_fiscal = models.TextField()
    regimen_fiscal = models.CharField(max_length=100)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Sucursal(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='sucursales')
    nombre = models.CharField(max_length=150)
    direccion = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"
        unique_together = ('empresa', 'nombre')
        ordering = ['empresa', 'nombre']
        indexes = [
            models.Index(fields=['empresa', 'nombre']),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.empresa.nombre})"
