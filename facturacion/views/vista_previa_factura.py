from django.http import FileResponse, Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from facturacion.models import ComprobanteFiscal

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def vista_previa_pdf(request, pk):
    try:
        comprobante = ComprobanteFiscal.objects.get(pk=pk)
        if not comprobante.pdf or not comprobante.pdf.path:
            raise Http404("PDF no disponible.")
        return FileResponse(open(comprobante.pdf.path, 'rb'), content_type='application/pdf')
    except ComprobanteFiscal.DoesNotExist:
        raise Http404("Comprobante no encontrado.")