# facturacion/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from facturacion.utils.validaciones import validar_datos_fiscales
from facturacion.models import ComprobanteFiscal

@api_view(['GET'])
def validar_datos_fiscales_view(request, venta_id):
    try:
        comprobante = ComprobanteFiscal.objects.get(venta_id=venta_id)
    except ComprobanteFiscal.DoesNotExist:
        return Response({"error": "Comprobante no encontrado para esta venta"}, status=404)

    resultado = validar_datos_fiscales(comprobante)
    if resultado["ok"]:
        return Response({"ok": True, "mensaje": "Todos los datos fiscales son válidos"})
    else:
        return Response({"ok": False, "errores": resultado["errores"]}, status=400)
