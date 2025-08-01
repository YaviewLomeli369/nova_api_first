# reportes/serializers/reportes_compras.py
from rest_framework import serializers

class DiasPromedioPagoProveedorSerializer(serializers.Serializer):
    proveedor = serializers.CharField()
    cantidad_pagos = serializers.IntegerField()
    dias_promedio_pago = serializers.DecimalField(max_digits=6, decimal_places=2)
