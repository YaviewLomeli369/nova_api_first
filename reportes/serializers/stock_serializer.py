from rest_framework import serializers

class StockActualProductoSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField(source='producto__id')
    producto_codigo = serializers.CharField(source='producto__codigo')
    producto_nombre = serializers.CharField(source='producto__nombre')
    categoria_id = serializers.IntegerField(source='producto__categoria__id')
    categoria_nombre = serializers.CharField(source='producto__categoria__nombre')
    stock_actual = serializers.DecimalField(max_digits=14, decimal_places=2)