from rest_framework import serializers
from django.db import transaction
from ventas.models import Venta, DetalleVenta
from inventario.models import Producto
from ventas.serializers.detalle_venta_serializer import DetalleVentaSerializer

class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Venta
        fields = [
            'id',
            'empresa',
            'cliente',
            'cliente_nombre',
            'usuario',
            'usuario_username',
            'fecha',
            'total',   # Calculado automáticamente por señal
            'estado',
            'detalles',
        ]
        read_only_fields = ['id', 'fecha', 'total']

    @transaction.atomic
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        venta = Venta.objects.create(**validated_data)

        for detalle_data in detalles_data:
            producto = Producto.objects.select_for_update().get(id=detalle_data['producto'].id)
            cantidad = detalle_data['cantidad']

            if producto.stock < cantidad:
                raise serializers.ValidationError(
                    f"No hay suficiente stock para el producto '{producto.nombre}'. Disponible: {producto.stock}"
                )

            producto.stock -= cantidad
            producto.save()

            DetalleVenta.objects.create(venta=venta, **detalle_data)

        return venta

    @transaction.atomic
    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if detalles_data is not None:
            for detalle in instance.detalles.all():
                producto = Producto.objects.select_for_update().get(id=detalle.producto.id)
                producto.stock += detalle.cantidad
                producto.save()

            instance.detalles.all().delete()

            for detalle_data in detalles_data:
                producto = Producto.objects.select_for_update().get(id=detalle_data['producto'].id)
                cantidad = detalle_data['cantidad']

                if producto.stock < cantidad:
                    raise serializers.ValidationError(
                        f"No hay suficiente stock para el producto '{producto.nombre}'. Disponible: {producto.stock}"
                    )

                producto.stock -= cantidad
                producto.save()

                DetalleVenta.objects.create(venta=instance, **detalle_data)

        return instance
