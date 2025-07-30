from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from facturacion.models import ComprobanteFiscal
from facturacion.services.timbrado_helpers import intentar_timbrado_comprobante
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reintentar_timbrado(request, comprobante_id):
    try:
        comprobante = ComprobanteFiscal.objects.get(id=comprobante_id)
    except ComprobanteFiscal.DoesNotExist:
        return Response({"error": "Comprobante no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if comprobante.estado == 'TIMBRADO':
        return Response({"error": "Comprobante ya está timbrado."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        intentar_timbrado_comprobante(comprobante)
        return Response({"message": "Timbrado exitoso.", "uuid": comprobante.uuid})
    except Exception as e:
        return Response({"error": f"Error al timbrar: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
