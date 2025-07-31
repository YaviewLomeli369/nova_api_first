# facturacion/views/envio_cfdi_viewset.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from facturacion.serializers.envio_cfdi import EnvioCorreoCFDISerializer
from facturacion.models import EnvioCorreoCFDI
from facturacion.filters import EnvioCorreoCFDIFilter
from rest_framework import filters

from django_filters.rest_framework import DjangoFilterBackend

class EnvioCorreoCFDIViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EnvioCorreoCFDI.objects.all().select_related("comprobante", "enviado_por")
    serializer_class = EnvioCorreoCFDISerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EnvioCorreoCFDIFilter
    search_fields = ['destinatario', 'comprobante__uuid', 'enviado_por__username']
    ordering_fields = ['fecha_envio']
    ordering = ['-fecha_envio']


# class EnvioCorreoCFDIViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = EnvioCorreoCFDI.objects.all().select_related("comprobante", "enviado_por")
#     serializer_class = EnvioCorreoCFDISerializer
#     permission_classes = [IsAuthenticated]
