# inventario/serializers.py
from rest_framework import serializers
from inventario.models import Inventario

class BatchSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = Inventario
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'fecha_vencimiento', 'ubicacion']
