from rest_framework import serializers
from ventas.models import DetalleVenta
from inventario.models import Inventario

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

        # Obtener todos los inventarios asociados al producto
        inventarios = Inventario.objects.filter(producto=producto)

        # Sumar la cantidad disponible de los inventarios
        stock_disponible = sum(inventario.cantidad for inventario in inventarios)

        # Verificar si hay suficiente stock
        if stock_disponible < cantidad:
            raise serializers.ValidationError(
                f"No hay suficiente stock para el producto '{producto.nombre}'. Stock disponible: {stock_disponible}"
            )

        return data
