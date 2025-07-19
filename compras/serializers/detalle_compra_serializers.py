# compras/serializers.py
from rest_framework import serializers
# from .models import  DetalleCompra
from compras.models import DetalleCompra
# from compras.serializers.detalle_compra_serializers import DetalleCompraSerializer

from inventario.models import Producto


class DetalleCompraSerializer(serializers.ModelSerializer):
    nombre_producto = serializers.CharField(source='producto.nombre', read_only=True)
    lote = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fecha_vencimiento = serializers.DateField(required=False, allow_null=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = DetalleCompra
        fields = [
            'id', 'producto', 'nombre_producto', 'cantidad', 'precio_unitario',
            'lote', 'fecha_vencimiento', 'subtotal'
        ]

    def get_subtotal(self, obj):
        return obj.subtotal
    

    def validate(self, data):
        producto = data.get('producto')
        cantidad = data.get('cantidad')
        precio_unitario = data.get('precio_unitario')

        if producto and not producto.activo:
            raise serializers.ValidationError("El producto seleccionado está inactivo.")

        if cantidad is not None and cantidad <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a cero.")

        if precio_unitario is not None and precio_unitario <= 0:
            raise serializers.ValidationError("El precio unitario debe ser mayor a cero.")

        return data