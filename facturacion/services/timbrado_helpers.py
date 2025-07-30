from django.utils import timezone
from facturacion.models import ComprobanteFiscal
from facturacion.services.facturama import FacturamaService
from facturacion.utils.build_facturama_payload import build_facturama_payload
from facturacion.utils.guardar_archivo_base64 import guardar_archivo_base64
from facturacion.utils.descargar_archivo_por_id import  descargar_archivo_por_id
from facturacion.utils.validaciones import validar_datos_fiscales



from django.utils import timezone
from facturacion.models import ComprobanteFiscal, TimbradoLog
from facturacion.services.facturama import FacturamaService
from facturacion.utils.build_facturama_payload import build_facturama_payload
from facturacion.utils.guardar_archivo_base64 import guardar_archivo_base64
from facturacion.utils.descargar_archivo_por_id import descargar_archivo_por_id
from facturacion.utils.validaciones import validar_datos_fiscales

def intentar_timbrado_comprobante(comprobante: ComprobanteFiscal, max_reintentos=3):
    # Sincronizar método y forma de pago desde venta
    comprobante.metodo_pago = comprobante.venta.metodo_pago or "PUE"
    comprobante.forma_pago = comprobante.venta.forma_pago or "01"
    comprobante.save()

    errores = validar_datos_fiscales(comprobante)
    if not errores["ok"]:
        raise Exception(f"Errores fiscales: {errores['errores']}")

    if comprobante.estado == 'TIMBRADO':
        return comprobante  # Ya está timbrado

    if comprobante.reintentos_timbrado >= max_reintentos:
        raise Exception(f"Máximo de {max_reintentos} reintentos alcanzado para el comprobante {comprobante.id}")

    payload = build_facturama_payload(comprobante)

    try:
        respuesta = FacturamaService.timbrar_comprobante(payload)

        uuid = respuesta.get('Complement', {}).get('TaxStamp', {}).get('Uuid')
        factura_id = respuesta.get('Id')

        comprobante.uuid = uuid
        comprobante.facturama_id = factura_id
        comprobante.estado = 'TIMBRADO'
        comprobante.fecha_timbrado = timezone.now()
        comprobante.error_mensaje = None
        comprobante.reintentos_timbrado += 1
        comprobante.fecha_ultimo_intento = timezone.now()

        xml_base64 = respuesta.get('Xml')
        if xml_base64:
            guardar_archivo_base64(xml_base64, comprobante, tipo='xml')
        elif factura_id:
            descargar_archivo_por_id(factura_id, comprobante, formato='xml')

        pdf_base64 = respuesta.get('Pdf')
        if pdf_base64:
            guardar_archivo_base64(pdf_base64, comprobante, tipo='pdf')
        elif factura_id:
            descargar_archivo_por_id(factura_id, comprobante, formato='pdf')

        comprobante.save()

        # Guardar registro de log de éxito
        TimbradoLog.objects.create(
            comprobante=comprobante,
            fecha_intento=timezone.now(),
            exito=True,
            mensaje_error=None,
            uuid_obtenido=uuid,
            facturama_id=factura_id,
        )

        return comprobante

    except Exception as e:
        comprobante.estado = 'ERROR'
        comprobante.error_mensaje = str(e)
        comprobante.reintentos_timbrado += 1
        comprobante.fecha_ultimo_intento = timezone.now()
        comprobante.save()

        # Guardar registro de log de error
        TimbradoLog.objects.create(
            comprobante=comprobante,
            fecha_intento=timezone.now(),
            exito=False,
            mensaje_error=str(e),
            uuid_obtenido=None,
            facturama_id=None,
        )

        raise e



# def intentar_timbrado_comprobante(comprobante: ComprobanteFiscal, max_reintentos=3):
#     # Sincronizar método y forma de pago desde venta
#     comprobante.metodo_pago = comprobante.venta.metodo_pago or "PUE"
#     comprobante.forma_pago = comprobante.venta.forma_pago or "01"
#     comprobante.save()

#     errores = validar_datos_fiscales(comprobante)
#     if not errores["ok"]:
#         raise Exception(f"Errores fiscales: {errores['errores']}")

#     if comprobante.estado == 'TIMBRADO':
#         return comprobante  # Ya está timbrado

#     if comprobante.reintentos_timbrado >= max_reintentos:
#         raise Exception(f"Máximo de {max_reintentos} reintentos alcanzado para el comprobante {comprobante.id}")

#     payload = build_facturama_payload(comprobante)

#     try:
#         respuesta = FacturamaService.timbrar_comprobante(payload)

#         uuid = respuesta.get('Complement', {}).get('TaxStamp', {}).get('Uuid')
#         factura_id = respuesta.get('Id')

#         comprobante.uuid = uuid
#         comprobante.facturama_id = factura_id
#         comprobante.estado = 'TIMBRADO'
#         comprobante.fecha_timbrado = timezone.now()
#         comprobante.error_mensaje = None
#         comprobante.reintentos_timbrado += 1
#         comprobante.fecha_ultimo_intento = timezone.now()

#         xml_base64 = respuesta.get('Xml')
#         if xml_base64:
#             guardar_archivo_base64(xml_base64, comprobante, tipo='xml')
#         elif factura_id:
#             descargar_archivo_por_id(factura_id, comprobante, formato='xml')

#         pdf_base64 = respuesta.get('Pdf')
#         if pdf_base64:
#             guardar_archivo_base64(pdf_base64, comprobante, tipo='pdf')
#         elif factura_id:
#             descargar_archivo_por_id(factura_id, comprobante, formato='pdf')

#         comprobante.save()
#         return comprobante

#     except Exception as e:
#         comprobante.estado = 'ERROR'
#         comprobante.error_mensaje = str(e)
#         comprobante.reintentos_timbrado += 1
#         comprobante.fecha_ultimo_intento = timezone.now()
#         comprobante.save()
#         raise e

