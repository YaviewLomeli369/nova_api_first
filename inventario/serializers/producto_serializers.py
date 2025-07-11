from rest_framework import serializers
from inventario.models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'empresa', 'codigo', 'nombre', 'descripcion', 'unidad_medida', 'categoria',
            'categoria_nombre', 'precio_compra', 'precio_venta', 'stock_minimo', 'activo'
        ]
        read_only_fields = ['id']

    def validate(self, data):
        precio_venta = data.get('precio_venta', getattr(self.instance, 'precio_venta', None))
        precio_compra = data.get('precio_compra', getattr(self.instance, 'precio_compra', None))

        if precio_venta is not None and precio_compra is not None:
            if precio_venta < precio_compra:
                raise serializers.ValidationError("El precio de venta no puede ser menor que el de compra.")

        return data
