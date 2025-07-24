# facturacion/services/timbrado.py
import datetime
import base64
from django.core.files.base import ContentFile
from facturacion.models import ComprobanteFiscal
from lxml import etree
from datetime import datetime
import requests
from xml.sax.saxutils import escape
from facturacion.utils.sat_firma import firmar_cadena, generar_cadena_original, cargar_certificado_base64
# from facturacion.helpers.facturama import timbrar_cfdi_emision
from facturacion.helpers.facturama import timbrar_cfdi_venta
from facturacion.models import ComprobanteFiscal

def validar_xml(xml_str: str, xsd_path: str):
    xml_doc = etree.fromstring(xml_str.encode('utf-8'))
    with open(xsd_path, 'rb') as f:
        schema_doc = etree.parse(f)
    schema = etree.XMLSchema(schema_doc)
    if not schema.validate(xml_doc):
        errores = [str(e) for e in schema.error_log]
        raise ValueError(f"Errores de validación XML: {errores}")




def guardar_xml_como_archivo(comprobante, contenido_xml: str):
    comprobante.xml.save(f"factura_{comprobante.id}.xml", ContentFile(contenido_xml.encode('utf-8')))



def enviar_a_pac(xml: str, token_api: str) -> dict:
    headers = {
        'Authorization': f'Bearer {token_api}',
        'Content-Type': 'application/xml'
    }
    response = requests.post('https://api.pac.example/timbrar', headers=headers, data=xml.encodea('utf-8'))
    if response.status_code == 200:
        return response.json()
    else:
        try:
            error_json = response.json()
        except Exception:
            error_json = {"detalle": response.text}
        raise Exception(f"Error PAC: {error_json}")
    

def guardar_pdf_base64(comprobante: ComprobanteFiscal, pdf_base64: str):
    """
    Decodifica el PDF y lo guarda como archivo en el modelo.
    """
    if pdf_base64:
        pdf_bytes = base64.b64decode(pdf_base64)
        comprobante.pdf.save(f"factura_{comprobante.id}.pdf",
                             ContentFile(pdf_bytes))

def generar_folio_siguiente(serie="A"):
    ultimo = ComprobanteFiscal.objects.filter(serie=serie).order_by("-folio").first()
    return (ultimo.folio + 1) if ultimo and ultimo.folio else 1


def timbrar_comprobante(comprobante):
    """
    Timbra un comprobante fiscal usando Facturama.
    """
    resultado = timbrar_cfdi_venta()

    if "error" in resultado:
        comprobante.estado = "ERROR"
        comprobante.mensaje_error = resultado["error"]
        comprobante.save()
    else:
        comprobante.estado = "TIMBRADO"
        comprobante.uuid = resultado.get("Complement", {}).get("TimbreFiscalDigital", {}).get("Uuid")
        comprobante.xml_timbrado = resultado.get("Xml")
        comprobante.save()

    return resultado
