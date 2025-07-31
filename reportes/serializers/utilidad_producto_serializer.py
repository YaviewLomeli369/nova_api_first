# reportes/serializers/utilidad_producto_serializer.py

from rest_framework import serializers

class UtilidadProductoOutputSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    nombre = serializers.CharField(source="producto__nombre")
    cantidad_vendida = serializers.FloatField()
    ingresos_ventas = serializers.FloatField()
    costo_total = serializers.FloatField()
    utilidad_bruta = serializers.FloatField()
