from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, Http404
from ventas.utils import generar_xml_desde_comprobante
from facturacion.models import ComprobanteFiscal


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vista_previa_xml(request, pk):
    try:
        comprobante = ComprobanteFiscal.objects.get(pk=pk)

        if comprobante.estado == 'TIMBRADO':
            return Response({"error": "Este comprobante ya está timbrado."}, status=status.HTTP_400_BAD_REQUEST)

        xml_bytes = generar_xml_desde_comprobante(comprobante)

        return HttpResponse(
            xml_bytes,
            content_type='application/xml'
        )

    except ComprobanteFiscal.DoesNotExist:
        raise Http404("Comprobante no encontrado.")
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
