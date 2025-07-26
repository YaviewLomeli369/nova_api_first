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

import base64
from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework.exceptions import ValidationError as DRFValidationError
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction

from facturacion.models import ComprobanteFiscal
from facturacion.services.facturama import FacturamaService
from facturacion.utils.build_facturama_payload import build_facturama_payload
from contabilidad.helpers.asientos import generar_asiento_para_venta
from finanzas.models import CuentaPorCobrar


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
        serie = 'A'  # Ejemplo, cambia por lógica real
        folio = 100  # Ejemplo, cambia por lógica real

        comprobante = ComprobanteFiscal.objects.create(
            empresa=empresa,
            venta=venta,
            estado='PENDIENTE',
            tipo='FACTURA',
            serie=serie,
            folio=folio
        )

        # 4. Crear payload para Facturama y timbrar
        payload = build_facturama_payload(comprobante)

        try:
            respuesta = FacturamaService.timbrar_comprobante(payload)

            uuid = respuesta.get('Complemento', {}).get('TimbreFiscalDigital', {}).get('UUID')
            fecha_timbrado_str = respuesta.get('FechaTimbrado')
            xml_base64 = respuesta.get('ArchivoXML')
            pdf_base64 = respuesta.get('ArchivoPDF')

            comprobante.uuid = uuid
            comprobante.estado = 'TIMBRADO'
            comprobante.fecha_timbrado = timezone.now()

            if xml_base64:
                xml_data = base64.b64decode(xml_base64)
                comprobante.xml.save(f'cfdi_{comprobante.id}.xml', ContentFile(xml_data), save=False)

            if pdf_base64:
                pdf_data = base64.b64decode(pdf_base64)
                comprobante.pdf.save(f'cfdi_{comprobante.id}.pdf', ContentFile(pdf_data), save=False)

            comprobante.save()

        except Exception as e:
            comprobante.estado = 'ERROR'
            comprobante.error_mensaje = str(e)
            comprobante.save()
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
