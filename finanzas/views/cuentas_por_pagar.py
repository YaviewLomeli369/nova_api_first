from rest_framework import viewsets, filters
from finanzas.models import CuentaPorPagar
from finanzas.serializers import CuentaPorPagarSerializer
from rest_framework.permissions import IsAuthenticated

class CuentaPorPagarViewSet(viewsets.ModelViewSet):
    """
    Listar cuentas por pagar con filtros por proveedor, estado y fecha de vencimiento.
    """
    queryset = CuentaPorPagar.objects.select_related('compra__proveedor').all()
    serializer_class = CuentaPorPagarSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['compra__proveedor__nombre']
    ordering_fields = ['fecha_vencimiento', 'estado']
    ordering = ['fecha_vencimiento']

    def get_queryset(self):
        qs = super().get_queryset()
        # Filtrar por estado
        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        # Filtrar por fecha_vencimiento (fecha exacta o rango?)
        fecha = self.request.query_params.get('fecha_vencimiento')
        if fecha:
            qs = qs.filter(fecha_vencimiento=fecha)
        return qs
