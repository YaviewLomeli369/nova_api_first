from django.core.files.base import ContentFile
from facturacion.services.facturama import FacturamaService


def descargar_archivo_por_id(factura_id, comprobante, formato='xml'):
    """
    Descarga el XML o PDF desde Facturama usando el ID de la factura.
    """
    try:
        if formato == 'xml':
            archivo_data = FacturamaService.obtener_xml_por_id(factura_id)
            comprobante.xml.save(f'cfdi_{comprobante.id}.xml', ContentFile(archivo_data), save=False)

        elif formato == 'pdf':
            archivo_data = FacturamaService.obtener_pdf_por_id(factura_id)
            comprobante.pdf.save(f'cfdi_{comprobante.id}.pdf', ContentFile(archivo_data), save=False)

        else:
            raise ValueError("Formato no soportado (solo 'xml' o 'pdf')")

    except Exception as e:
        raise Exception(f"Error al descargar archivo {formato} por ID: {str(e)}")
