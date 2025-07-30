from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from facturacion.models import ComprobanteFiscal, TimbradoLog
from facturacion.serializers.timbrado import TimbradoLogSerializer
from rest_framework.exceptions import NotFound

class TimbradoLogListView(generics.ListAPIView):
    serializer_class = TimbradoLogSerializer
    permission_classes = [IsAuthenticated]  # o déjalo abierto si quieres

    def get_queryset(self):
        comprobante_id = self.kwargs.get('comprobante_id')
        try:
            comprobante = ComprobanteFiscal.objects.get(id=comprobante_id)
        except ComprobanteFiscal.DoesNotExist:
            raise NotFound("Comprobante no encontrado")

        return comprobante.logs_timbrado.all()
