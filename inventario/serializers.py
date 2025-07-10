# inventario/serializers.py

from rest_framework import serializers
from .models import Categoria, Producto, Inventario, MovimientoInventario

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ['id']


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

        # Solo validar si ambos valores están disponibles
        if precio_venta is not None and precio_compra is not None:
            if precio_venta < precio_compra:
                raise serializers.ValidationError("El precio de venta no puede ser menor que el de compra.")

        return data

    # def validate(self, data):
    #     if data['precio_venta'] < data['precio_compra']:
    #         raise serializers.ValidationError("El precio de venta no puede ser menor que el de compra.")
    #     return data


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


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoInventario
        fields = '__all__'

    def validate(self, data):
        producto = data['producto']
        tipo = data['tipo']
        cantidad = data['cantidad']

        if tipo == 'salida' and producto.stock < cantidad:
            raise serializers.ValidationError("Stock insuficiente para salida.")

        return data

    def create(self, validated_data):
        producto = validated_data['producto']
        tipo = validated_data['tipo']
        cantidad = validated_data['cantidad']

        # Actualiza el stock
        if tipo == 'entrada':
            producto.stock += cantidad
        elif tipo == 'salida':
            producto.stock -= cantidad
        elif tipo == 'ajuste':
            producto.stock = cantidad  # Ajuste directo

        producto.save()
        return super().create(validated_data)