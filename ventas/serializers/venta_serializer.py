from rest_framework import serializers
from ventas.models import Venta, DetalleVenta
from .detalle_venta_serializer import DetalleVentaSerializer
from inventario.models import Producto, Inventario
from contabilidad.helpers.asientos import generar_asiento_para_venta
from finanzas.models import CuentaPorCobrar
from django.db import transaction
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.db.models import F

def redondear_decimal(valor, decimales=2):
    if not isinstance(valor, Decimal):
        valor = Decimal(str(valor))
    return valor.quantize(Decimal('1.' + '0' * decimales), rounding=ROUND_HALF_UP)

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

        if usuario is None:
            raise DRFValidationError("Usuario no autenticado.")
        if empresa is None:
            raise DRFValidationError("El usuario no tiene una empresa asignada.")

        venta = Venta(**validated_data)
        venta.usuario = usuario
        venta.empresa = empresa
        venta.save()

        detalles = []
        total_calculado = Decimal('0.00')

        for detalle_data in detalles_data:
            try:
                producto = Producto.objects.get(id=detalle_data['producto'].id)
            except Producto.DoesNotExist:
                raise DRFValidationError(f"Producto con id {detalle_data['producto'].id} no existe.")

            cantidad = detalle_data.get('cantidad')
            precio_unitario = detalle_data.get('precio_unitario')

            # Validaciones básicas
            if cantidad is None or cantidad <= 0:
                raise DRFValidationError(f"La cantidad para el producto '{producto.nombre}' debe ser mayor a cero.")
            if precio_unitario is None or precio_unitario <= 0:
                raise DRFValidationError(f"El precio unitario para el producto '{producto.nombre}' debe ser mayor a cero.")

            inventario = Inventario.objects.select_for_update().filter(
                producto=producto,
                sucursal__empresa=empresa
            ).first()

            if not inventario:
                raise DRFValidationError(
                    f"No hay inventario disponible para el producto '{producto.nombre}'"
                )
            if inventario.cantidad < cantidad:
                raise DRFValidationError(
                    f"No hay suficiente stock para el producto '{producto.nombre}'. Disponible: {inventario.cantidad}"
                )

            # Actualizar inventario con select_for_update para evitar race conditions
            inventario.cantidad = F('cantidad') - cantidad
            inventario.save()
            inventario.refresh_from_db()

            detalle = DetalleVenta(venta=venta, **detalle_data)
            detalles.append(detalle)

            total_calculado += cantidad * precio_unitario

        DetalleVenta.objects.bulk_create(detalles)

        venta.total = redondear_decimal(total_calculado)
        venta.save(update_fields=['total'])

        # Crear CuentaPorCobrar automáticamente
        fecha_vencimiento = venta.fecha + timedelta(days=30)  # plazo 30 días
        CuentaPorCobrar.objects.create(
            empresa=empresa,
            venta=venta,
            monto=venta.total,
            fecha_vencimiento=fecha_vencimiento,
            estado='PENDIENTE'
        )

        try:
            generar_asiento_para_venta(venta, usuario)
        except Exception as e:
            # Aquí puedes loggear el error o tomar alguna acción adicional
            raise DRFValidationError(f"Error al generar asiento contable: {str(e)}")

        return venta
# from rest_framework import serializers
# from ventas.models import Venta, DetalleVenta
# from .detalle_venta_serializer import DetalleVentaSerializer
# from inventario.models import Producto, Inventario
# from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable
# from django.db import transaction
# from datetime import timedelta
# from finanzas.models import CuentaPorCobrar
# from decimal import Decimal, ROUND_HALF_UP
# from contabilidad.helpers.asientos import generar_asiento_para_venta
# from rest_framework.exceptions import ValidationError as DRFValidationError

# def redondear_decimal(valor, decimales=2):
#     if not isinstance(valor, Decimal):
#         valor = Decimal(str(valor))
#     return valor.quantize(Decimal('1.' + '0' * decimales), rounding=ROUND_HALF_UP)

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

#         request = self.context.get('request')
#         usuario = request.user if request else None
#         empresa = getattr(usuario, 'empresa', None)

#         venta = Venta(**validated_data)
#         venta.usuario = usuario
#         venta.empresa = empresa
#         venta.save()

#         detalles = []
#         total_calculado = 0

#         for detalle_data in detalles_data:
#             try:
#                 producto = Producto.objects.get(id=detalle_data['producto'].id)
#             except Producto.DoesNotExist:
#                 raise DRFValidationError(f"Producto con id {detalle_data['producto'].id} no existe.")

#             cantidad = detalle_data['cantidad']

#             inventario = Inventario.objects.filter(
#                 producto=producto,
#                 sucursal__empresa=empresa
#             ).first()

#             if not inventario:
#                 raise DRFValidationError(
#                     f"No hay inventario disponible para el producto '{producto.nombre}'"
#                 )
#             if inventario.cantidad < cantidad:
#                 raise DRFValidationError(
#                     f"No hay suficiente stock para el producto '{producto.nombre}'. Disponible: {inventario.cantidad}"
#                 )
#             inventario.cantidad -= cantidad
#             inventario.save()

#             detalle = DetalleVenta(venta=venta, **detalle_data)
#             detalles.append(detalle)
#             total_calculado += cantidad * detalle_data['precio_unitario']

#         DetalleVenta.objects.bulk_create(detalles)

#         venta.total = total_calculado
#         venta.save(update_fields=['total'])

#         # Crear CuentaPorCobrar automáticamente
#         fecha_vencimiento = venta.fecha + timedelta(days=30)  # plazo 30 días
#         CuentaPorCobrar.objects.create(
#             empresa=empresa,
#             venta=venta,
#             monto=total_calculado,
#             fecha_vencimiento=fecha_vencimiento,
#             estado='PENDIENTE'
#         )

#         try:
#             generar_asiento_para_venta(venta, usuario)
#         except Exception as e:
#             # Opcional: aquí podrías revertir la venta o loggear el error
#             raise DRFValidationError(f"Error al generar asiento contable: {str(e)}")

#         return venta


