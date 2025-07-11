from rest_framework import serializers
from inventario.models import Inventario

class InventarioSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)

    class Meta:
        model = Inventario
        fields = [
            'id', 'producto', 'producto_nombre', 'sucursal', 'sucursal_nombre',
            'lote', 'fecha_vencimiento', 'cantidad'
        ]
        read_only_fields = ['id']

    def validate_cantidad(self, value):
        if value < 0:
            raise serializers.ValidationError("La cantidad no puede ser negativa.")
        return value
