from rest_framework import serializers
from ventas.models import DetalleVenta

class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = DetalleVenta
        fields = [
            'id',
            'producto',
            'producto_nombre',
            'cantidad',
            'precio_unitario',
            'subtotal',
        ]

    def get_subtotal(self, obj):
        return obj.cantidad * obj.precio_unitario

    def validate(self, data):
        cantidad = data.get('cantidad')
        precio_unitario = data.get('precio_unitario')
        producto = data.get('producto')

        if cantidad is None or cantidad <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a cero.")
        if precio_unitario is None or precio_unitario <= 0:
            raise serializers.ValidationError("El precio unitario debe ser mayor a cero.")
        if producto is None:
            raise serializers.ValidationError("El producto es obligatorio.")

        if producto.stock < cantidad:
            raise serializers.ValidationError(
                f"No hay suficiente stock para el producto '{producto.nombre}'. Stock disponible: {producto.stock}"
            )

        return data
