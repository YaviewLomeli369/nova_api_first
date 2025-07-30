from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from facturacion.models import ComprobanteFiscal
from facturacion.utils.enviar_correo import enviar_cfdi_por_correo
import re

def es_email_valido(correo):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", correo))


@csrf_exempt
def reenviar_email_cfdi(request, uuid):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        comprobante = ComprobanteFiscal.objects.select_related('venta__cliente').get(uuid=uuid)
    except ComprobanteFiscal.DoesNotExist:
        return JsonResponse({"error": "Comprobante no encontrado"}, status=404)

    if comprobante.estado == 'CANCELADO':
        return JsonResponse({
            "error": "El comprobante ya fue cancelado y no puede ser reenviado."
        }, status=400)

    if not comprobante.xml or not comprobante.pdf:
        return JsonResponse({
            "error": "No se puede reenviar: faltan archivos PDF o XML"
        }, status=400)

    cliente_email = comprobante.venta.cliente.correo
    copia_email = "yaview.lomeli@gmail.com"

    errores = []

    if es_email_valido(cliente_email):
        try:
            enviar_cfdi_por_correo(cliente_email, comprobante)
        except Exception as e:
            errores.append(f"Error al enviar a cliente: {e}")
    else:
        errores.append("Correo del cliente inválido.")

    if es_email_valido(copia_email):
        try:
            enviar_cfdi_por_correo(copia_email, comprobante)
        except Exception as e:
            errores.append(f"Error al enviar a copia: {e}")

    if errores:
        return JsonResponse({
            "message": "Reenvío incompleto",
            "errores": errores
        }, status=207)

    return JsonResponse({"message": "Correo reenviado correctamente"})
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from facturacion.models import ComprobanteFiscal
# from facturacion.utils.enviar_correo import enviar_cfdi_por_correo  # ✅ usa el correcto
# import re

# def es_email_valido(correo):
#     return bool(re.match(r"[^@]+@[^@]+\.[^@]+", correo))
    
# @csrf_exempt
# def reenviar_email_cfdi(request, uuid):
#     if request.method != 'POST':
#         return JsonResponse({"error": "Método no permitido"}, status=405)

#     try:
#         comprobante = ComprobanteFiscal.objects.get(uuid=uuid)
#     except ComprobanteFiscal.DoesNotExist:
#         return JsonResponse({"error": "Comprobante no encontrado"}, status=404)

#     if comprobante.estado == 'CANCELADO':
#         return JsonResponse({
#             "error": "El comprobante ya fue cancelado y no puede ser reenviado."
#         }, status=400)

#     if not comprobante.xml or not comprobante.pdf:
#         return JsonResponse({
#             "error": "No se puede reenviar: faltan archivos PDF o XML"
#         }, status=400)

#     # Correos a enviar
#     cliente_email = comprobante.venta.cliente.correo
#     copia_email = "yaview.lomeli@gmail.com"

#     errores = []

#     # Validar y enviar a cliente
#     if es_email_valido(cliente_email):
#         try:
#             enviar_cfdi_por_correo(cliente_email, comprobante)
#         except Exception as e:
#             errores.append(f"Error al enviar a cliente: {e}")
#     else:
#         errores.append("Correo del cliente inválido.")

#     # Validar y enviar copia si estás en pruebas
#     if es_email_valido(copia_email):
#         try:
#             enviar_cfdi_por_correo(copia_email, comprobante)
#         except Exception as e:
#             errores.append(f"Error al enviar a copia: {e}")

#     if errores:
#         return JsonResponse({
#             "message": "Reenvío incompleto",
#             "errores": errores
#         }, status=207)  # Multi-status (algunos fallaron)

#     return JsonResponse({"message": "Correo reenviado correctamente"})

    # try:
    #     cliente_email = comprobante.venta.cliente.correo
    #     cliente_email_2 = "yaview.lomeli@gmail.com"
    #     enviar_cfdi_por_correo(cliente_email, comprobante)
    #     enviar_cfdi_por_correo(cliente_email_2, comprobante)
    #     return JsonResponse({"message": "Correo reenviado correctamente"})
    # except Exception as e:
    #     return JsonResponse({
    #         "error": "Error al reenviar correo",
    #         "detalle": str(e)
    #     }, status=500)

# # facturacion/views/reenviar_email_cfdi.py

# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from facturacion.models import ComprobanteFiscal
# from facturacion.utils.enviar_correo import enviar_cfdi_por_correo

# @csrf_exempt
# def reenviar_email_cfdi(request, uuid):
#     if request.method != 'POST':
#         return JsonResponse({"error": "Método no permitido"}, status=405)

#     try:
#         comprobante = ComprobanteFiscal.objects.get(uuid=uuid)
#     except ComprobanteFiscal.DoesNotExist:
#         return JsonResponse({"error": "Comprobante no encontrado"}, status=404)

#     if not comprobante.xml or not comprobante.pdf:
#         return JsonResponse({
#             "error": "No se puede reenviar: faltan archivos PDF o XML"
#         }, status=400)

#     try:
#         enviar_cfdi_por_correo(comprobante)
#         return JsonResponse({"message": "Correo reenviado correctamente"})
#     except Exception as e:
#         return JsonResponse({
#             "error": "Error al reenviar correo",
#             "detalle": str(e)
#         }, status=500)
