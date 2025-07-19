from finanzas.models import CuentaPorCobrar
from finanzas.serializers import CuentaPorCobrarSerializer
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

class CuentaPorCobrarViewSet(viewsets.ModelViewSet):
    """
    Listar cuentas por cobrar con filtros por cliente, estado y fecha de vencimiento.
    """
    queryset = CuentaPorCobrar.objects.select_related('venta__cliente').all()
    serializer_class = CuentaPorCobrarSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['venta__cliente__nombre']
    ordering_fields = ['fecha_vencimiento', 'estado']
    ordering = ['fecha_vencimiento']

    def get_queryset(self):
        qs = super().get_queryset()
        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        fecha = self.request.query_params.get('fecha_vencimiento')
        if fecha:
            qs = qs.filter(fecha_vencimiento=fecha)
        return qs
