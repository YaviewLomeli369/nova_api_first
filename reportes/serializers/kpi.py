# reportes/serializers/kpi.py
from rest_framework import serializers

class RentabilidadProductoClienteSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    producto__nombre = serializers.CharField()
    venta__cliente_id = serializers.IntegerField()
    venta__cliente__nombre = serializers.CharField()
    total_venta = serializers.DecimalField(max_digits=20, decimal_places=2)
    costo_venta = serializers.DecimalField(max_digits=20, decimal_places=2)
    utilidad_total = serializers.DecimalField(max_digits=20, decimal_places=2)
