from django.utils import timezone
from facturacion.models import ComprobanteFiscal

def intentar_timbrado_comprobante(comprobante: ComprobanteFiscal, max_reintentos=3):
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

        # Aquí guardas XML/PDF igual que ya haces (base64 o descarga por ID)...

        comprobante.save()
        return comprobante

    except Exception as e:
        comprobante.estado = 'ERROR'
        comprobante.error_mensaje = str(e)
        comprobante.reintentos_timbrado += 1
        comprobante.fecha_ultimo_intento = timezone.now()
        comprobante.save()
        raise e
