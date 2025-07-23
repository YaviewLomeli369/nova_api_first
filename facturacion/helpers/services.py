# facturacion/services.py
import datetime
from django.core.files.base import ContentFile
from facturacion.models import ComprobanteFiscal

def generar_xml(comprobante: ComprobanteFiscal) -> str:
    # TODO: Generar XML con librería o plantilla según datos de comprobante y venta
    xml = f"<cfdi>Ejemplo XML para venta {comprobante.venta.id}</cfdi>"
    return xml

def enviar_pac(xml: str) -> dict:
    # TODO: Implementar llamada real a PAC (sandbox o prod)
    # Ejemplo mock respuesta exitosa:
    response = {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "fecha_timbrado": datetime.datetime.now().isoformat(),
        "pdf": b"PDFbytes_en_base64_o_binario",
        "estado": "TIMBRADO",
        "error": None
    }
    return response

def timbrar_comprobante(comprobante: ComprobanteFiscal) -> ComprobanteFiscal:
    # Generar XML
    xml = generar_xml(comprobante)
    comprobante.xml = xml
    comprobante.save()

    # Enviar a PAC
    respuesta = enviar_pac(xml)

    if respuesta["estado"] == "TIMBRADO":
        comprobante.uuid = respuesta["uuid"]
        comprobante.fecha_timbrado = respuesta["fecha_timbrado"]
        comprobante.estado = "TIMBRADO"
        # Guardar PDF (ejemplo: guardar bytes recibidos en archivo)
        if respuesta.get("pdf"):
            from django.core.files.base import ContentFile
            comprobante.pdf.save(f"factura_{comprobante.id}.pdf", ContentFile(respuesta["pdf"]))
        comprobante.error_mensaje = None
    else:
        comprobante.estado = "ERROR"
        comprobante.error_mensaje = respuesta.get("error", "Error desconocido")

    comprobante.save()
    return comprobante
