# facturacion/views/acuses.py

from django.http import FileResponse, JsonResponse
from facturacion.models import ComprobanteFiscal
import os

def descargar_acuse_cancelacion(request, uuid):
    try:
        cfdi = ComprobanteFiscal.objects.get(uuid=uuid)
    except ComprobanteFiscal.DoesNotExist:
        return JsonResponse({"error": "Comprobante no encontrado"}, status=404)

    if not cfdi.acuse_cancelacion_xml:
        return JsonResponse({"error": "No hay acuse de cancelación disponible"}, status=404)

    if not os.path.exists(cfdi.acuse_cancelacion_xml.path):
        return JsonResponse({"error": "Archivo de acuse no encontrado"}, status=404)

    return FileResponse(open(cfdi.acuse_cancelacion_xml.path, 'rb'), content_type='application/xml')
