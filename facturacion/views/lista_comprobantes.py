# views.py

from rest_framework import generics
from facturacion.models import ComprobanteFiscal
from facturacion.serializers.comprobante_fiscal import ComprobanteFiscalSerializer
from rest_framework.permissions import IsAuthenticated

class ComprobanteFiscalListView(generics.ListAPIView):
    queryset = ComprobanteFiscal.objects.all()
    serializer_class = ComprobanteFiscalSerializer
    permission_classes = [IsAuthenticated]

    # Filtros, puedes adaptarlo a tus necesidades
    def get_queryset(self):
        queryset = super().get_queryset()
        # Aquí puedes agregar filtros, por ejemplo, por estado o tipo de comprobante
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset
