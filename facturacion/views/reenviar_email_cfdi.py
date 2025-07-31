from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status

from facturacion.models import ComprobanteFiscal, EnvioCorreoCFDI
from facturacion.utils.enviar_correo import enviar_cfdi_por_correo
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

Usuario = get_user_model()

def obtener_usuario_sistema():
    return Usuario.objects.filter(username='sistema').first()

def es_email_valido(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def reenviar_email_cfdi(request, uuid):
    try:
        comprobante = ComprobanteFiscal.objects.select_related('venta__cliente').get(uuid=uuid)
    except ComprobanteFiscal.DoesNotExist:
        return Response({"error": "Comprobante no encontrado"}, status=404)

    if comprobante.estado == 'CANCELADO':
        return Response({"error": "El comprobante ya fue cancelado y no puede ser reenviado."}, status=400)

    if not comprobante.xml or not comprobante.pdf:
        return Response({"error": "No se puede reenviar: faltan archivos PDF o XML"}, status=400)

    cliente_email = comprobante.venta.cliente.correo
    copia_email = "yaview.lomeli@gmail.com"
    errores = []

    enviado_por = request.user if request and request.user.is_authenticated else obtener_usuario_sistema()

    if es_email_valido(cliente_email):
        try:
            enviar_cfdi_por_correo(cliente_email, comprobante)
            EnvioCorreoCFDI.objects.create(
                comprobante=comprobante,
                destinatario=cliente_email,
                enviado_por=enviado_por
            )
        except Exception as e:
            errores.append(f"Error al enviar a cliente: {str(e)}")
    else:
        errores.append("Correo del cliente inválido.")

    if es_email_valido(copia_email):
        try:
            enviar_cfdi_por_correo(copia_email, comprobante)
            EnvioCorreoCFDI.objects.create(
                comprobante=comprobante,
                destinatario=copia_email,
                enviado_por=enviado_por
            )
        except Exception as e:
            errores.append(f"Error al enviar a copia: {str(e)}")

    if errores:
        return Response({
            "message": "Reenvío incompleto",
            "errores": errores
        }, status=207)

    return Response({"message": "Correo reenviado correctamente"}, status=200)

# from rest_framework.decorators import api_view, authentication_classes, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.response import Response
# from rest_framework import status

# from facturacion.models import ComprobanteFiscal, EnvioCorreoCFDI
# from facturacion.utils.enviar_correo import enviar_cfdi_por_correo
# from django.contrib.auth import get_user_model
# import re

# Usuario = get_user_model()

# def obtener_usuario_sistema():
#     return Usuario.objects.filter(username='sistema').first()

# def es_email_valido(correo):
#     return bool(re.match(r"[^@]+@[^@]+\.[^@]+", correo))


# @api_view(['POST'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
# def reenviar_email_cfdi(request, uuid):
#     try:
#         comprobante = ComprobanteFiscal.objects.select_related('venta__cliente').get(uuid=uuid)
#     except ComprobanteFiscal.DoesNotExist:
#         return Response({"error": "Comprobante no encontrado"}, status=404)

#     if comprobante.estado == 'CANCELADO':
#         return Response({"error": "El comprobante ya fue cancelado y no puede ser reenviado."}, status=400)

#     if not comprobante.xml or not comprobante.pdf:
#         return Response({"error": "No se puede reenviar: faltan archivos PDF o XML"}, status=400)

#     cliente_email = comprobante.venta.cliente.correo
#     copia_email = "yaview.lomeli@gmail.com"
#     errores = []

#     if es_email_valido(cliente_email):
#         try:
#             enviar_cfdi_por_correo(cliente_email, comprobante)
#             EnvioCorreoCFDI.objects.create(
#                 comprobante=comprobante,
#                 destinatario=cliente_email,
#                 enviado_por=request.user
#             )
#         except Exception as e:
#             errores.append(f"Error al enviar a cliente: {str(e)}")
#     else:
#         errores.append("Correo del cliente inválido.")

#     if es_email_valido(copia_email):
#         try:
#             enviar_cfdi_por_correo(copia_email, comprobante)
#             EnvioCorreoCFDI.objects.create(
#                 comprobante=comprobante,
#                 destinatario=copia_email,
#                 enviado_por=request.user
#             )
#         except Exception as e:
#             errores.append(f"Error al enviar a copia: {str(e)}")

#     if errores:
#         return Response({
#             "message": "Reenvío incompleto",
#             "errores": errores
#         }, status=207)

#     return Response({"message": "Correo reenviado correctamente"}, status=200)
