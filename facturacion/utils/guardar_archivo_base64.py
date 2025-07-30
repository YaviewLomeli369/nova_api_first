import base64
from django.core.files.base import ContentFile


def guardar_archivo_base64(base64_str, comprobante, tipo='xml'):
    """
    Guarda un archivo base64 (XML o PDF) en el campo del comprobante correspondiente.
    """
    try:
        decoded_data = base64.b64decode(base64_str)

        if tipo == 'xml':
            comprobante.xml.save(f'cfdi_{comprobante.id}.xml', ContentFile(decoded_data), save=False)
        elif tipo == 'pdf':
            comprobante.pdf.save(f'cfdi_{comprobante.id}.pdf', ContentFile(decoded_data), save=False)
        else:
            raise ValueError("Tipo de archivo no soportado")

    except Exception as e:
        raise Exception(f"Error al guardar archivo {tipo} desde base64: {str(e)}")
