import xml.etree.ElementTree as ET
from django.core.files.base import ContentFile
from django.utils import timezone

def generar_xml_desde_comprobante(comprobante):
    """
    Genera un XML básico desde un objeto comprobante.
    Ajusta esto según el estándar fiscal (ej. CFDI, UBL, etc.).
    """
    # Estructura básica del XML
    root = ET.Element("Comprobante")
    ET.SubElement(root, "UUID").text = comprobante.uuid if hasattr(comprobante, 'uuid') else "UUID-Generico"
    ET.SubElement(root, "Fecha").text = timezone.now().isoformat()
    ET.SubElement(root, "Total").text = str(comprobante.total)

    # Agrega otros campos relevantes aquí
    # ...

    # Convierte el árbol a una cadena de bytes
    xml_string = ET.tostring(root, encoding="utf-8", method="xml")

    # Opcional: Guarda el XML en el modelo (si tiene campo FileField)
    if hasattr(comprobante, 'archivo_xml'):
        comprobante.archivo_xml.save(f"{comprobante.id}.xml", ContentFile(xml_string), save=True)

    return xml_string