from rest_framework import serializers
from django.db import transaction
from ventas.models import Venta, DetalleVenta
from inventario.models import Producto, Inventario
from ventas.serializers.detalle_venta_serializer import DetalleVentaSerializer
from datetime import timedelta
from finanzas.models import CuentaPorCobrar

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

        request = self.context.get('request')
        usuario = request.user if request else None
        empresa = getattr(usuario, 'empresa', None)

        venta = Venta(**validated_data)
        venta.usuario = usuario
        venta.empresa = empresa
        venta.save()

        detalles = []
        total_calculado = 0

        for detalle_data in detalles_data:
            producto = Producto.objects.get(id=detalle_data['producto'].id)
            cantidad = detalle_data['cantidad']

            inventario = Inventario.objects.filter(
                producto=producto,
                sucursal__empresa=empresa
            ).first()

            if not inventario:
                raise serializers.ValidationError(
                    f"No hay inventario disponible para el producto '{producto.nombre}'"
                )
            if inventario.cantidad < cantidad:
                raise serializers.ValidationError(
                    f"No hay suficiente stock para el producto '{producto.nombre}'. Disponible: {inventario.cantidad}"
                )
            inventario.cantidad -= cantidad
            inventario.save()

            detalle = DetalleVenta(venta=venta, **detalle_data)
            detalles.append(detalle)
            total_calculado += cantidad * detalle_data['precio_unitario']

        DetalleVenta.objects.bulk_create(detalles)

        venta.total = total_calculado
        venta.save(update_fields=['total'])

        # Crear CuentaPorCobrar automáticamente
        fecha_vencimiento = venta.fecha + timedelta(days=30)  # plazo 30 días
        CuentaPorCobrar.objects.create(
            empresa=empresa,
            venta=venta,
            monto=total_calculado,
            fecha_vencimiento=fecha_vencimiento,
            estado='PENDIENTE'
        )

        return venta

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

#         # Crear la venta pero aún no la guardamos
#         venta = Venta(**validated_data)

#         # Guardar la venta inicialmente con total=0 para obtener su ID
#         venta.save()

#         # Ahora que la venta tiene un ID, procesamos los detalles
#         detalles = []
#         total_calculado = 0
        
#         for detalle_data in detalles_data:
#             producto = Producto.objects.get(id=detalle_data['producto'].id)
#             cantidad = detalle_data['cantidad']

#             # Obtener el inventario del producto para la empresa del usuario
#             from inventario.models import Inventario
#             try:
#                 # Buscar inventario del producto en cualquier sucursal de la empresa
#                 inventario = Inventario.objects.filter(
#                     producto=producto,
#                     sucursal__empresa=validated_data['empresa']
#                 ).first()
                
#                 if not inventario:
#                     raise serializers.ValidationError(
#                         f"No hay inventario disponible para el producto '{producto.nombre}'"
#                     )
                
#                 # Verificar si hay suficiente stock
#                 if inventario.cantidad < cantidad:
#                     raise serializers.ValidationError(
#                         f"No hay suficiente stock para el producto '{producto.nombre}'. Disponible: {inventario.cantidad}"
#                     )

#                 # Reducir el stock del inventario
#                 inventario.cantidad -= cantidad
#                 inventario.save()
                
#             except Inventario.DoesNotExist:
#                 raise serializers.ValidationError(
#                     f"No hay inventario disponible para el producto '{producto.nombre}'"
#                 )

#             # Crear los detalles de la venta
#             detalle = DetalleVenta(
#                 venta=venta,
#                 **detalle_data
#             )
#             detalles.append(detalle)
            
#             # Calcular el subtotal y agregarlo al total
#             total_calculado += detalle_data['cantidad'] * detalle_data['precio_unitario']

#         # Guardar todos los detalles de la venta
#         DetalleVenta.objects.bulk_create(detalles)

#         # Actualizar el total de la venta directamente
#         venta.total = total_calculado
#         venta.save(update_fields=['total'])

#         return venta

