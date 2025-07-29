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
from django.conf import settings
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

        # 4. Crear payload para Facturama y timbrar
        payload = build_facturama_payload(comprobante)

        try:
            respuesta = FacturamaService.timbrar_comprobante(payload)

            uuid = respuesta.get('Complement', {}).get('TaxStamp', {}).get('Uuid')
            factura_id = respuesta.get('Id')
            comprobante.uuid = uuid
            comprobante.estado = 'TIMBRADO'
            comprobante.fecha_timbrado = timezone.now()

            # Detectar si es sandbox o producción
            is_sandbox = 'sandbox' in settings.FACTURAMA_API_URL

            if is_sandbox:
                # En sandbox, usar base64 devuelto por timbrado
                archivo_xml_b64 = respuesta.get('ArchivoXML')
                archivo_pdf_b64 = respuesta.get('ArchivoPDF')

                if archivo_xml_b64:
                    xml_data = base64.b64decode(archivo_xml_b64)
                    comprobante.xml.save(f'cfdi_{comprobante.id}.xml', ContentFile(xml_data), save=False)
                if archivo_pdf_b64:
                    pdf_data = base64.b64decode(archivo_pdf_b64)
                    comprobante.pdf.save(f'cfdi_{comprobante.id}.pdf', ContentFile(pdf_data), save=False)
            else:
                # En producción, descargar vía GET usando factura_id
                archivo_pdf = FacturamaService.obtener_pdf_por_id(factura_id)
                archivo_xml = FacturamaService.obtener_xml_por_id(factura_id)
                comprobante.xml.save(f'cfdi_{comprobante.id}.xml', ContentFile(archivo_xml), save=False)
                comprobante.pdf.save(f'cfdi_{comprobante.id}.pdf', ContentFile(archivo_pdf), save=False)

            comprobante.save()

        except Exception as descarga_error:
            # No marcar ERROR si el timbrado fue exitoso pero hubo problema con archivos
            comprobante.error_mensaje = f"Timbrado correcto, pero error con archivos: {str(descarga_error)}"
            comprobante.save()


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

        import json
        print("Payload enviado a Facturama:")
        print(json.dumps(payload, indent=2))
        print("Respuesta de Facturama:")
        print(json.dumps(respuesta, indent=2))
        print("Respuesta Facturama completa:", respuesta)
        
        return venta
