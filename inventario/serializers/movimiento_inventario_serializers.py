from rest_framework import serializers
from inventario.models import MovimientoInventario

class MovimientoInventarioSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='inventario.producto.nombre', read_only=True)
    producto_codigo = serializers.CharField(source='inventario.producto.codigo', read_only=True)
    sucursal_nombre = serializers.CharField(source='inventario.sucursal.nombre', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    tipo_movimiento_display = serializers.CharField(source='get_tipo_movimiento_display', read_only=True)
    
    class Meta:
        model = MovimientoInventario
        fields = [
            'id', 'tipo_movimiento', 'tipo_movimiento_display', 'cantidad', 'fecha',
            'inventario', 'usuario', 'producto_nombre', 'producto_codigo', 
            'sucursal_nombre', 'usuario_username'
        ]

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

        if tipo == 'entrada':
            producto.stock += cantidad
        elif tipo == 'salida':
            producto.stock -= cantidad
        elif tipo == 'ajuste':
            producto.stock = cantidad  # Ajuste directo

        producto.save()
        return super().create(validated_data)
