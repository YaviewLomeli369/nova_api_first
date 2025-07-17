from rest_framework import serializers
from compras.models import Proveedor, Compra, DetalleCompra
from compras.serializers.detalle_compra_serializers import DetalleCompraSerializer
from inventario.models import Inventario, MovimientoInventario


class CompraSerializer(serializers.ModelSerializer):
    detalles = DetalleCompraSerializer(many=True)
    total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    nombre_proveedor = serializers.CharField(source='proveedor.nombre', read_only=True)

    class Meta:
        model = Compra
        fields = [
            'id', 'empresa', 'proveedor', 'nombre_proveedor', 'fecha', 'estado',
            'usuario', 'total', 'detalles'
        ]
        read_only_fields = ['id', 'total']

    def validate(self, data):
        if data.get('estado') not in dict(Compra.ESTADO_CHOICES):
            raise serializers.ValidationError("Estado inválido.")
        return data

    def create(self, validated_data):
        request = self.context['request']
        usuario = request.user
        sucursal = getattr(usuario, 'sucursal_actual', None)

        if not sucursal:
            raise serializers.ValidationError("El usuario no tiene una sucursal asignada.")

        detalles_data = validated_data.pop('detalles')
        total = 0

        compra = Compra.objects.create(**validated_data)

        for detalle_data in detalles_data:
            producto = detalle_data['producto']
            cantidad = detalle_data['cantidad']
            precio_unitario = detalle_data['precio_unitario']

            # Crear detalle
            DetalleCompra.objects.create(
                compra=compra,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario
            )

            total += cantidad * precio_unitario

            # Obtener o crear inventario
            inventario, creado = Inventario.objects.get_or_create(
                producto=producto,
                sucursal=sucursal,
                lote=None,
                fecha_vencimiento=None,
                defaults={'cantidad': 0}
            )

            # Actualizar stock
            inventario.cantidad += cantidad
            inventario.save()

            # Registrar movimiento de inventario
            MovimientoInventario.objects.create(
                inventario=inventario,
                tipo_movimiento='entrada',
                cantidad=cantidad,
                usuario=usuario
            )

        compra.total = total
        compra.save()
        return compra

    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if detalles_data is not None:
            instance.detalles.all().delete()
            total = 0
            for detalle_data in detalles_data:
                detalle = DetalleCompra.objects.create(compra=instance, **detalle_data)
                total += detalle.cantidad * detalle.precio_unitario
            instance.total = total

        instance.save()
        return instance

# from rest_framework import serializers
# from compras.models import Proveedor, Compra, DetalleCompra
# from compras.serializers.detalle_compra_serializers import DetalleCompraSerializer


# class CompraSerializer(serializers.ModelSerializer):
#   detalles = DetalleCompraSerializer(many=True)
#   total = serializers.DecimalField(max_digits=14,
#                                    decimal_places=2,
#                                    read_only=True)
#   nombre_proveedor = serializers.CharField(source='proveedor.nombre',
#                                            read_only=True)

#   class Meta:
#     model = Compra
#     fields = [
#         'id', 'empresa', 'proveedor', 'nombre_proveedor', 'fecha', 'estado',
#         'usuario', 'total', 'detalles'
#     ]
#     read_only_fields = ['id', 'total']

#   def validate(self, data):
#     if data.get('estado') not in dict(Compra.ESTADO_CHOICES):
#       raise serializers.ValidationError("Estado inválido.")
#     return data

#   def create(self, validated_data):
#     detalles_data = validated_data.pop('detalles')
#     total = 0

#     compra = Compra.objects.create(**validated_data)

#     for detalle_data in detalles_data:
#       detalle = DetalleCompra.objects.create(compra=compra, **detalle_data)
#       total += detalle.cantidad * detalle.precio_unitario

#     compra.total = total
#     compra.save()

#     return compra

#   def update(self, instance, validated_data):
#     detalles_data = validated_data.pop('detalles', None)

#     for attr, value in validated_data.items():
#       setattr(instance, attr, value)

#     if detalles_data is not None:
#       instance.detalles.all().delete()
#       total = 0
#       for detalle_data in detalles_data:
#         detalle = DetalleCompra.objects.create(compra=instance, **detalle_data)
#         total += detalle.cantidad * detalle.precio_unitario
#       instance.total = total

#     instance.save()
#     return instance