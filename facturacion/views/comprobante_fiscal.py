from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from facturacion.models import ComprobanteFiscal
from facturacion.serializers.comprobante_fiscal import ComprobanteFiscalSerializer
from facturacion.services.consultar_estado_cfdi import consultar_estado_cfdi

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from facturacion.filters import ComprobanteFiscalFilter  # si lo pones en un archivo filters.py

class ComprobanteFiscalViewSet(viewsets.ModelViewSet):
    queryset = ComprobanteFiscal.objects.all()
    serializer_class = ComprobanteFiscalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ComprobanteFiscalFilter  # Usamos el FilterSet personalizado

    @action(detail=True, methods=["get"])
    def actualizar_estado_sat(self, request, pk=None):
        comprobante = self.get_object()

        if not comprobante.esta_timbrado():
            return Response({"error": "El comprobante no está timbrado."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            resultado = consultar_estado_cfdi(
                uuid=comprobante.uuid,
                issuer_rfc=comprobante.empresa.rfc,
                receiver_rfc=comprobante.venta.cliente.rfc,
                total=comprobante.venta.total
            )

            comprobante.estado_sat = resultado.get("Estado")
            comprobante.fecha_estado_sat = timezone.now()
            comprobante.save(update_fields=["estado_sat", "fecha_estado_sat"])

            return Response({
                "uuid": comprobante.uuid,
                "estado_sat": comprobante.estado_sat,
                "fecha_estado_sat": comprobante.fecha_estado_sat,
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
