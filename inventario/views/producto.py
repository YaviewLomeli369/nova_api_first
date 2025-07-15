from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from inventario.models import Producto
from inventario.serializers import ProductoSerializer
from inventario.filters import ProductoFilter
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions

class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

    queryset = Producto.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductoFilter

    search_fields = ['codigo', 'nombre', 'descripcion', 'codigo_barras', 'lote']
    ordering_fields = ['nombre', 'precio_venta', 'stock', 'fecha_vencimiento']
    ordering = ['nombre']

    def get_queryset(self):
        return Producto.objects.filter(empresa=self.request.user.empresa)



