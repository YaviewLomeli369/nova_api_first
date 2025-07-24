from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from facturacion.models import ComprobanteFiscal
from facturacion.serializers.comprobantes import ComprobanteFiscalSerializer
from facturacion.services.timbrado import timbrar_comprobante



class ComprobanteFiscalViewSet(viewsets.ModelViewSet):
    queryset = ComprobanteFiscal.objects.all()
    serializer_class = ComprobanteFiscalSerializer

    @action(detail=True, methods=['post'])
    def timbrar(self, request, pk=None):
        comprobante = self.get_object()
        if comprobante.estado == 'TIMBRADO':
            return Response({"detail": "Comprobante ya timbrado."}, status=status.HTTP_400_BAD_REQUEST)

        comprobante = timbrar_comprobante(comprobante)
        serializer = self.get_serializer(comprobante)
        return Response(serializer.data)