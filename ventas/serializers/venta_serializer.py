from rest_framework import serializers
from django.db import transaction
from ventas.models import Venta, DetalleVenta
from inventario.models import Producto, Inventario
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
            'total',
            'estado',
            'detalles',
        ]
        read_only_fields = ['id', 'fecha', 'total']

    @transaction.atomic
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')

        # Crear la venta pero aún no la guardamos
        venta = Venta(**validated_data)

        # Guardar la venta inicialmente con total=0 para obtener su ID
        venta.save()

        # Ahora que la venta tiene un ID, procesamos los detalles
        detalles = []
        total_calculado = 0
        
        for detalle_data in detalles_data:
            producto = Producto.objects.get(id=detalle_data['producto'].id)
            cantidad = detalle_data['cantidad']

            # Obtener el inventario del producto para la empresa del usuario
            from inventario.models import Inventario
            try:
                # Buscar inventario del producto en cualquier sucursal de la empresa
                inventario = Inventario.objects.filter(
                    producto=producto,
                    sucursal__empresa=validated_data['empresa']
                ).first()
                
                if not inventario:
                    raise serializers.ValidationError(
                        f"No hay inventario disponible para el producto '{producto.nombre}'"
                    )
                
                # Verificar si hay suficiente stock
                if inventario.cantidad < cantidad:
                    raise serializers.ValidationError(
                        f"No hay suficiente stock para el producto '{producto.nombre}'. Disponible: {inventario.cantidad}"
                    )

                # Reducir el stock del inventario
                inventario.cantidad -= cantidad
                inventario.save()
                
            except Inventario.DoesNotExist:
                raise serializers.ValidationError(
                    f"No hay inventario disponible para el producto '{producto.nombre}'"
                )

            # Crear los detalles de la venta
            detalle = DetalleVenta(
                venta=venta,
                **detalle_data
            )
            detalles.append(detalle)
            
            # Calcular el subtotal y agregarlo al total
            total_calculado += detalle_data['cantidad'] * detalle_data['precio_unitario']

        # Guardar todos los detalles de la venta
        DetalleVenta.objects.bulk_create(detalles)

        # Actualizar el total de la venta directamente
        venta.total = total_calculado
        venta.save(update_fields=['total'])

        return venta



# from rest_framework import serializers
# from django.db import transaction
# from ventas.models import Venta, DetalleVenta
# from inventario.models import Producto
# from ventas.serializers.detalle_venta_serializer import DetalleVentaSerializer

# class VentaSerializer(serializers.ModelSerializer):
#     detalles = DetalleVentaSerializer(many=True)
#     cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
#     usuario_username = serializers.CharField(source='usuario.username', read_only=True)

#     class Meta:
#         model = Venta
#         fields = [
#             'id',
#             'empresa',
#             'cliente',
#             'cliente_nombre',
#             'usuario',
#             'usuario_username',
#             'fecha',
#             'total',
#             'estado',
#             'detalles',
#         ]
#         read_only_fields = ['id', 'fecha', 'total']

#     @transaction.atomic
#     def create(self, validated_data):
#         detalles_data = validated_data.pop('detalles')

#         # Crear la venta sin guardarla inicialmente
#         venta = Venta(**validated_data)

#         # Guarda la venta para que se genere el ID de la venta
#         venta.save()

#         # Verificamos si el ID de la venta es correcto
#         if not venta.id:
#             raise serializers.ValidationError("La venta no pudo generar un ID correctamente.")

#         detalles = []
#         for detalle_data in detalles_data:
#             producto = Producto.objects.select_for_update().get(id=detalle_data['producto'].id)
#             cantidad = detalle_data['cantidad']

#             if producto.stock < cantidad:
#                 raise serializers.ValidationError(
#                     f"No hay suficiente stock para el producto '{producto.nombre}'. Disponible: {producto.stock}"
#                 )

#             producto.stock -= cantidad
#             producto.save()

#             # Crear los objetos DetalleVenta pero no guardarlos aún
#             detalle = DetalleVenta(venta=venta, **detalle_data)
#             detalles.append(detalle)

#         # Guardar todos los detalles de la venta a la vez usando bulk_create
#         DetalleVenta.objects.bulk_create(detalles)

#         # Después de guardar los detalles, asegurarnos de calcular y guardar el total de la venta
#         venta.calcular_total()
#         venta.save()

#         return venta

