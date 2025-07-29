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
from facturacion.models import MetodoPagoChoices, FormaPagoChoices
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


            payment_method = respuesta.get("PaymentMethod")
            payment_form = respuesta.get("PaymentForm")

            # Validar contra enums antes de asignar
            if payment_method in MetodoPagoChoices.values:
                comprobante.metodo_pago = payment_method
            else:
                comprobante.error_mensaje = f"Método de pago no válido: {payment_method}"

            if payment_form in FormaPagoChoices.values:
                comprobante.forma_pago = payment_form
            else:
                comprobante.error_mensaje = f"Forma de pago no válida: {payment_form}"

            # Detectar si es sandbox o producción
            is_sandbox = 'sandbox' in settings.FACTURAMA_API_URL.lower()
            print(f"DEBUG: Es sandbox: {is_sandbox}")
            print(f"DEBUG: API URL: {settings.FACTURAMA_API_URL}")
            print(f"DEBUG: Factura ID recibido: {factura_id}")

            # Intentar guardar archivos
            archivos_guardados = False

            try:
                # Primero intentar usar archivos base64 de la respuesta de timbrado (si están disponibles)
                archivo_xml_b64 = respuesta.get('ArchivoXML')
                archivo_pdf_b64 = respuesta.get('ArchivoPDF')

                print(f"DEBUG: XML base64 en respuesta: {bool(archivo_xml_b64)}")
                print(f"DEBUG: PDF base64 en respuesta: {bool(archivo_pdf_b64)}")

                xml_guardado = False
                pdf_guardado = False

                # Intentar guardar XML desde base64 de respuesta
                if archivo_xml_b64:
                    try:
                        xml_data = base64.b64decode(archivo_xml_b64)
                        print(f"DEBUG: Guardando XML desde respuesta base64, tamaño: {len(xml_data)} bytes")
                        comprobante.xml.save(f'cfdi_{comprobante.id}.xml', ContentFile(xml_data), save=False)
                        xml_guardado = True
                    except Exception as e:
                        print(f"DEBUG: Error guardando XML desde respuesta base64: {e}")

                # Intentar guardar PDF desde base64 de respuesta
                if archivo_pdf_b64:
                    try:
                        pdf_data = base64.b64decode(archivo_pdf_b64)
                        print(f"DEBUG: Guardando PDF desde respuesta base64, tamaño: {len(pdf_data)} bytes")
                        comprobante.pdf.save(f'cfdi_{comprobante.id}.pdf', ContentFile(pdf_data), save=False)
                        pdf_guardado = True
                    except Exception as e:
                        print(f"DEBUG: Error guardando PDF desde respuesta base64: {e}")

                # Si no se pudieron guardar desde la respuesta, descargar por ID
                if factura_id and (not xml_guardado or not pdf_guardado):
                    print("DEBUG: Descargando archivos faltantes por ID de Facturama")
                    try:
                        if not xml_guardado:
                            print("DEBUG: Descargando XML por ID...")
                            archivo_xml = FacturamaService.obtener_xml_por_id(factura_id)
                            comprobante.xml.save(f'cfdi_{comprobante.id}.xml', ContentFile(archivo_xml), save=False)
                            xml_guardado = True
                            print(f"DEBUG: XML descargado y guardado, tamaño: {len(archivo_xml)} bytes")

                        if not pdf_guardado:
                            print("DEBUG: Descargando PDF por ID...")
                            archivo_pdf = FacturamaService.obtener_pdf_por_id(factura_id)
                            comprobante.pdf.save(f'cfdi_{comprobante.id}.pdf', ContentFile(archivo_pdf), save=False)
                            pdf_guardado = True
                            print(f"DEBUG: PDF descargado y guardado, tamaño: {len(archivo_pdf)} bytes")

                    except Exception as e:
                        print(f"DEBUG: Error descargando archivos por ID: {e}")
                        comprobante.error_mensaje = f"Error descargando archivos: {str(e)}"

                archivos_guardados = xml_guardado and pdf_guardado

                print(f"DEBUG: Archivos guardados exitosamente: {archivos_guardados}")
                print(f"DEBUG: Guardando comprobante con ID: {comprobante.id}")
                comprobante.save()
                print(f"DEBUG: Comprobante guardado. XML: {bool(comprobante.xml)}, PDF: {bool(comprobante.pdf)}")

            except Exception as descarga_error:
                print(f"DEBUG: Error general en manejo de archivos: {descarga_error}")
                # No marcar ERROR si el timbrado fue exitoso pero hubo problema con archivos
                comprobante.error_mensaje = f"Timbrado correcto, pero error con archivos: {str(descarga_error)}"
                comprobante.save()


        except Exception as e:
            print(f"DEBUG: Error al timbrar comprobante: {e}")
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

        import json
        print("Payload enviado a Facturama:")
        print(json.dumps(payload, indent=2))
        print("Respuesta de Facturama:")
        print(json.dumps(respuesta, indent=2))
        print("Respuesta Facturama completa:", respuesta)

        return venta