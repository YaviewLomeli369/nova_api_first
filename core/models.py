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
    razon_social = models.CharField(max_length=255, blank=True, null=True)  # Añadido razon_social



    domicilio_calle = models.CharField(max_length=150)
    domicilio_num_ext = models.CharField(max_length=10, blank=True, null=True)
    domicilio_num_int = models.CharField(max_length=10, blank=True, null=True)
    domicilio_colonia = models.CharField(max_length=100)
    domicilio_municipio = models.CharField(max_length=100)
    domicilio_estado = models.CharField(max_length=100)
    domicilio_pais = models.CharField(max_length=50, default='MEX')
    domicilio_codigo_postal = models.CharField(max_length=10)

    def get_direccion_formateada(self):
        partes = [
            self.domicilio_calle,
            f"Ext. {self.domicilio_num_ext}" if self.domicilio_num_ext else None,
            f"Int. {self.domicilio_num_int}" if self.domicilio_num_int else None,
            self.domicilio_colonia,
            self.domicilio_municipio,
            self.domicilio_estado,
            self.domicilio_pais,
            self.domicilio_codigo_postal,
        ]
        # Eliminar None o vacíos y unir con coma
        return ", ".join(filter(None, partes))
    

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Sucursal(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='sucursales')
    nombre = models.CharField(max_length=150)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    domicilio_calle = models.CharField(max_length=150)
    domicilio_num_ext = models.CharField(max_length=10, blank=True, null=True)
    domicilio_num_int = models.CharField(max_length=10, blank=True, null=True)
    domicilio_colonia = models.CharField(max_length=100)
    domicilio_municipio = models.CharField(max_length=100)
    domicilio_estado = models.CharField(max_length=100)
    domicilio_pais = models.CharField(max_length=50, default='MEX')
    domicilio_codigo_postal = models.CharField(max_length=10)

    def get_direccion_formateada(self):
        partes = [
            self.domicilio_calle,
            f"Ext. {self.domicilio_num_ext}" if self.domicilio_num_ext else None,
            f"Int. {self.domicilio_num_int}" if self.domicilio_num_int else None,
            self.domicilio_colonia,
            self.domicilio_municipio,
            self.domicilio_estado,
            self.domicilio_pais,
            self.domicilio_codigo_postal,
        ]
        # Eliminar None o vacíos y unir con coma
        return ", ".join(filter(None, partes))

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
