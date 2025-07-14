from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from inventario.models import MovimientoInventario
from inventario.serializers import MovimientoInventarioSerializer

from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions

class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

    def get_queryset(self):
        user = self.request.user
        return MovimientoInventario.objects.filter(producto__empresa=user.empresa).order_by('-fecha')

# # inventario/views/movimiento.py

# from rest_framework import viewsets
# from inventario.models import MovimientoInventario
# from inventario.serializers import MovimientoInventarioSerializer

# class MovimientoInventarioViewSet(viewsets.ModelViewSet):  # ✅ debe ser ModelViewSet
#     queryset = MovimientoInventario.objects.all()
#     serializer_class = MovimientoInventarioSerializer
