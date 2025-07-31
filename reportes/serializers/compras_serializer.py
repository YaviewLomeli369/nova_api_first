from rest_framework import serializers

class ReporteComprasProveedorSerializer(serializers.Serializer):
    proveedor_id = serializers.IntegerField(source='proveedor__id')
    proveedor_nombre = serializers.CharField(source='proveedor__nombre')
    total_compras = serializers.DecimalField(max_digits=14, decimal_places=2)
    num_compras = serializers.IntegerField()
