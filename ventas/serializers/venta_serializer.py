from rest_framework import serializers
from ventas.models import Venta, DetalleVenta
from .detalle_venta_serializer import DetalleVentaSerializer
from inventario.models import Producto, Inventario
from contabilidad.helpers.asientos import generar_asiento_para_venta
from django.db import transaction
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import F
from django.conf import settings
import base64
from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework.exceptions import ValidationError as DRFValidationError
from facturacion.models import MetodoPagoChoices, FormaPagoChoices, ComprobanteFiscal
from facturacion.services.facturama import FacturamaService
from facturacion.utils.build_facturama_payload import build_facturama_payload
# from facturacion.utils.build_facturama_payload import MetodoPagoChoices
from finanzas.models import CuentaPorCobrar
from django.db.models import TextChoices

from facturacion.services.timbrado_helpers import intentar_timbrado_comprobante

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
            'forma_pago',
            'metodo_pago',
            'condiciones_pago',
            'detalles'
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

        # 1. Crear la venta
        venta = Venta(**validated_data)
        venta.usuario = usuario
        venta.empresa = empresa
        venta.save()

        # 2. Crear detalles y actualizar inventario
        total_calculado = Decimal('0.00')
        detalles = []

        for detalle_data in detalles_data:
            producto = detalle_data['producto']
            cantidad = detalle_data.get('cantidad')
            precio_unitario = detalle_data.get('precio_unitario')

            inventario = Inventario.objects.select_for_update().filter(
                producto=producto,
                sucursal__empresa=empresa
            ).first()

            if not inventario:
                raise DRFValidationError(f"No hay inventario para el producto {producto.nombre}")

            if inventario.cantidad < cantidad:
                raise DRFValidationError(f"Stock insuficiente para producto {producto.nombre}")

            inventario.cantidad = F('cantidad') - cantidad
            inventario.save()
            inventario.refresh_from_db()

            detalle = DetalleVenta(venta=venta, **detalle_data)
            detalles.append(detalle)

            total_calculado += cantidad * precio_unitario

        DetalleVenta.objects.bulk_create(detalles)

        venta.total = redondear_decimal(total_calculado)
        venta.save(update_fields=['total'])

        

        # 3. Crear ComprobanteFiscal en PENDIENTE
        def generar_folio(empresa):
            ultimo = ComprobanteFiscal.objects.filter(empresa=empresa, serie='A').order_by('-folio').first()
            return (ultimo.folio + 1) if ultimo and ultimo.folio else 1
            
        serie = 'A'
        folio = generar_folio(empresa)


        # Guardar primero para asegurar que comprobante.id esté disponible
        comprobante = ComprobanteFiscal.objects.create(
            empresa=empresa,
            venta=venta,
            estado='PENDIENTE',
            tipo='FACTURA',
            serie=serie,
            folio=folio
        )

        # Forzar guardado si estás inseguro de que tenga ID
        if not comprobante.id:
            comprobante.save()




        try:
            intentar_timbrado_comprobante(comprobante)
        except Exception as e:
            raise DRFValidationError(f"Error al timbrar comprobante: {str(e)}")

        # 5. Crear CuentaPorCobrar
        fecha_vencimiento = venta.fecha + timedelta(days=30)
        CuentaPorCobrar.objects.create(
            empresa=empresa,
            venta=venta,
            monto=venta.total,
            fecha_vencimiento=fecha_vencimiento,
            estado='PENDIENTE'
        )

        # 6. Generar asiento contable
        try:
            generar_asiento_para_venta(venta, usuario)
        except Exception as e:
            raise DRFValidationError(f"Error al generar asiento contable: {str(e)}")



        return venta