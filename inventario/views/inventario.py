from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from inventario.models import Inventario
from inventario.serializers import InventarioSerializer

from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions

class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.select_related('producto', 'sucursal')
    serializer_class = InventarioSerializer
    permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(producto__empresa=user.empresa)
