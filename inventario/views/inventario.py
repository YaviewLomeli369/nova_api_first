# inventario/views/inventario.py

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from inventario.models import Inventario
from inventario.serializers import InventarioSerializer
from inventario.filters import InventarioFilter
from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions

class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.select_related('producto', 'sucursal')
    serializer_class = InventarioSerializer
    permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = InventarioFilter
    search_fields = ['producto__nombre', 'sucursal__nombre']  # Búsqueda libre
    ordering_fields = ['cantidad', 'producto__nombre', 'sucursal__nombre']
    ordering = ['-cantidad']  # Orden por defecto

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(producto__empresa=user.empresa)

# from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated
# from inventario.models import Inventario
# from inventario.serializers import InventarioSerializer

# from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions

# class InventarioViewSet(viewsets.ModelViewSet):
#     queryset = Inventario.objects.select_related('producto', 'sucursal')
#     serializer_class = InventarioSerializer
#     permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

#     def get_queryset(self):
#         user = self.request.user
#         return self.queryset.filter(producto__empresa=user.empresa)
