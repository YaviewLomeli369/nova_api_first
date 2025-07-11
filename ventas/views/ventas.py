from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from ventas.models import Venta
from ventas.serializers import VentaSerializer

class VentaViewSet(viewsets.ModelViewSet):
    """
    CRUD para Ventas, con detalles anidados.
    """
    queryset = Venta.objects.all().select_related('cliente', 'usuario', 'empresa').prefetch_related('detalles')
    serializer_class = VentaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['cliente__nombre', 'usuario__username', 'estado']
    filterset_fields = ['empresa', 'estado', 'fecha', 'cliente']

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
