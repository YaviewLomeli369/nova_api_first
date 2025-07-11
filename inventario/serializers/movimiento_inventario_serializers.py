from rest_framework import serializers
from inventario.models import MovimientoInventario

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

        if tipo == 'entrada':
            producto.stock += cantidad
        elif tipo == 'salida':
            producto.stock -= cantidad
        elif tipo == 'ajuste':
            producto.stock = cantidad  # Ajuste directo

        producto.save()
        return super().create(validated_data)
