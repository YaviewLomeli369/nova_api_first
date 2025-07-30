# facturacion/views/cancelar_factura.py

import requests
import base64
from django.utils.timezone import now
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from facturacion.models import ComprobanteFiscal
from django.conf import settings

@csrf_exempt
def cancelar_cfdi(request, uuid):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        cfdi = ComprobanteFiscal.objects.get(uuid=uuid)
    except ComprobanteFiscal.DoesNotExist:
        return JsonResponse({"error": "CFDI no encontrado"}, status=404)

    if cfdi.estado == 'CANCELADO':
        return JsonResponse({"message": "El CFDI ya fue cancelado"}, status=400)

    # Validar que tengas el ID de Facturama (no UUID)
    factura_id = getattr(cfdi, 'facturama_id', None)
    if not factura_id:
        return JsonResponse({"error": "No se encontró el ID de Facturama en el comprobante."}, status=400)

    # Parámetros requeridos
    motive = cfdi.motivo_cancelacion or "02"
    uuid_replacement = cfdi.sustitucion_uuid or ""
    cancel_type = "issued"

    # Autenticación básica
    api_key = f'{settings.FACTURAMA_USER}:{settings.FACTURAMA_PASSWORD}'
    api_key_encoded = base64.b64encode(api_key.encode()).decode()
    headers = {
        "Authorization": f"Basic {api_key_encoded}",
        "Content-Type": "application/json"
    }

    url = f'https://apisandbox.facturama.mx/cfdi/{factura_id}?type={cancel_type}&motive={motive}&uuidReplacement={uuid_replacement}'
    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        cfdi.estado = 'CANCELADO'
        cfdi.fecha_cancelacion = now()

        # Si hay acuse XML, guárdalo en disco
        acuse_b64 = data.get("AcuseXmlBase64")
        if acuse_b64:
            acuse_bytes = base64.b64decode(acuse_b64)
            filename = f"acuse_{cfdi.uuid}.xml"
            cfdi.acuse_cancelacion_xml.save(filename, ContentFile(acuse_bytes))

        cfdi.save()

        return JsonResponse({
            "message": "CFDI cancelado correctamente",
            "status": data.get("Status"),
            "uuid": data.get("Uuid"),
            "acuse_xml": bool(acuse_b64)
        })

    try:
        detalles = response.json()
    except Exception:
        detalles = response.text or {}

    return JsonResponse({
        "error": "Error al cancelar CFDI",
        "status_code": response.status_code,
        "detalles": detalles
    }, status=400)

# import requests
# import base64
# from django.utils.timezone import now
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from facturacion.models import ComprobanteFiscal
# from django.conf import settings
# from django.views.decorators.csrf import csrf_exempt

# # facturacion/views.py

# @csrf_exempt
# def cancelar_cfdi(request, uuid):
#     try:
#         cfdi = ComprobanteFiscal.objects.get(uuid=uuid)
#     except ComprobanteFiscal.DoesNotExist:
#         return JsonResponse({"error": "CFDI no encontrado"}, status=404)

#     if cfdi.estado == 'CANCELADO':
#         return JsonResponse({"message": "El CFDI ya fue cancelado"}, status=400)

#     # Validar que tengas el ID de Facturama (no UUID)
#     factura_id = getattr(cfdi, 'facturama_id', None)
#     if not factura_id:
#         return JsonResponse({"error": "No se encontró el ID de Facturama en el comprobante."}, status=400)

#     # Parámetros requeridos
#     motive = cfdi.motivo_cancelacion or "02"
#     uuid_replacement = cfdi.sustitucion_uuid or ""
#     cancel_type = "issued"  # o "Received" dependiendo del rol; normalmente "Issued"

#     # Autenticación básica
#     api_key = f'{settings.FACTURAMA_USER}:{settings.FACTURAMA_PASSWORD}'
#     api_key_encoded = base64.b64encode(api_key.encode()).decode()
#     headers = {
#         "Authorization": f"Basic {api_key_encoded}",
#         "Content-Type": "application/json"
#     }

#     url = f'https://apisandbox.facturama.mx/cfdi/{factura_id}?type={cancel_type}&motive={motive}&uuidReplacement={uuid_replacement}'

#     response = requests.delete(url, headers=headers)

#     if response.status_code == 200:
#         cfdi.estado = 'CANCELADO'
#         cfdi.fecha_cancelacion = now()
#         cfdi.save()
#         return JsonResponse({"message": "CFDI cancelado correctamente"})
#     else:
#         try:
#             detalles = response.json()
#         except Exception:
#             detalles = response.text or {}
#         return JsonResponse({
#             "error": "Error al cancelar CFDI",
#             "status_code": response.status_code,
#             "detalles": detalles
#         }, status=400)

