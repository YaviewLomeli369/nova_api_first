from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from ventas.models import DetalleVenta
from ventas.serializers import DetalleVentaSerializer

class DetalleVentaViewSet(viewsets.ModelViewSet):
    """
    CRUD para Detalles de Venta
    """
    queryset = DetalleVenta.objects.all().select_related('venta', 'producto')
    serializer_class = DetalleVentaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['venta', 'producto']
