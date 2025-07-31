from django.utils import timezone
from facturacion.models import ComprobanteFiscal
from facturacion.services.facturama import FacturamaService
from facturacion.utils.build_facturama_payload import build_facturama_payload
from facturacion.utils.guardar_archivo_base64 import guardar_archivo_base64
from facturacion.utils.descargar_archivo_por_id import  descargar_archivo_por_id
from facturacion.utils.validaciones import validar_datos_fiscales
from facturacion.utils.enviar_correo import enviar_cfdi_por_correo
import re


from django.utils import timezone
from facturacion.models import ComprobanteFiscal, TimbradoLog
from facturacion.services.facturama import FacturamaService
from facturacion.utils.build_facturama_payload import build_facturama_payload
from facturacion.utils.guardar_archivo_base64 import guardar_archivo_base64
from facturacion.utils.descargar_archivo_por_id import descargar_archivo_por_id
from facturacion.utils.validaciones import validar_datos_fiscales
from facturacion.models import EnvioCorreoCFDI
from django.contrib.auth import get_user_model
Usuario = get_user_model()

def obtener_usuario_sistema():
    return Usuario.objects.filter(username='sistema').first()
    

def intentar_timbrado_comprobante(comprobante: ComprobanteFiscal, request=None, max_reintentos=3):

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

        # Enviar correo con CFDI adjunto
        try:
            cliente_email = comprobante.venta.cliente.correo
            cliente_email_2 = "yaview.lomeli@gmail.com"
            enviado_por = (
                request.user if request and hasattr(request, 'user') and request.user.is_authenticated
                else obtener_usuario_sistema()
            )

            if cliente_email:
                print(comprobante)
                enviar_cfdi_por_correo(cliente_email, comprobante)
                EnvioCorreoCFDI.objects.create(
                    comprobante=comprobante,
                    destinatario=cliente_email,
                    enviado_por=enviado_por
                )

            if cliente_email_2:
                enviar_cfdi_por_correo(cliente_email_2, comprobante)
                EnvioCorreoCFDI.objects.create(
                    comprobante=comprobante,
                    destinatario=cliente_email_2,
                    enviado_por=enviado_por
                )
                

        except Exception as e:
            # Solo loguea el error, no interrumpas el flujo
            print(f"Error enviando correo: {e}")

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
