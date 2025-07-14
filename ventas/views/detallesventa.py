# from rest_framework import viewsets, permissions
# from django_filters.rest_framework import DjangoFilterBackend
# from ventas.models import DetalleVenta
# from ventas.serializers import DetalleVentaSerializer
# from accounts.permissions import IsVendedor, IsEmpresaAdmin

# class DetalleVentaViewSet(viewsets.ModelViewSet):
#     """
#     CRUD para Detalles de Venta
#     """
#     queryset = DetalleVenta.objects.all().select_related('venta', 'producto')
#     serializer_class = DetalleVentaSerializer
#     permission_classes = [permissions.IsAuthenticated & (IsVendedor | IsEmpresaAdmin)]
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['venta', 'producto']
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from ventas.models import DetalleVenta
from ventas.serializers import DetalleVentaSerializer
from accounts.permissions import IsVendedor, IsEmpresaAdmin

class DetalleVentaViewSet(viewsets.ModelViewSet):
    """
    CRUD para Detalles de Venta
    """
    queryset = DetalleVenta.objects.all().select_related('venta', 'producto')
    serializer_class = DetalleVentaSerializer
    permission_classes = [permissions.IsAuthenticated & (IsVendedor | IsEmpresaAdmin)]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['venta', 'producto']

    def get_queryset(self):
        user = self.request.user
        if user.rol.nombre == "Superadministrador":
            return self.queryset
        # Filtrar detalles solo de ventas pertenecientes a la empresa del usuario
        return self.queryset.filter(venta__empresa=user.empresa)
