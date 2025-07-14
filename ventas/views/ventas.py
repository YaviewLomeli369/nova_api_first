from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from ventas.models import Venta
from ventas.serializers import VentaSerializer
from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsVendedor

class VentaViewSet(viewsets.ModelViewSet):
    """
    CRUD para Ventas, con detalles anidados.
    """
    queryset = Venta.objects.all().select_related('cliente', 'usuario', 'empresa').prefetch_related('detalles')
    serializer_class = VentaSerializer
    permission_classes = [permissions.IsAuthenticated & (IsSuperAdmin | IsEmpresaAdmin | IsVendedor)]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['cliente__nombre', 'usuario__username', 'estado']
    filterset_fields = ['empresa', 'estado', 'fecha', 'cliente']

    def get_queryset(self):
        user = self.request.user
        if user.rol.nombre == "Superadministrador":
            return self.queryset
        return self.queryset.filter(empresa=user.empresa)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)




# from rest_framework import viewsets, permissions, filters
# from django_filters.rest_framework import DjangoFilterBackend
# from ventas.models import Venta
# from ventas.serializers import VentaSerializer

# class VentaViewSet(viewsets.ModelViewSet):
#     """
#     CRUD para Ventas, con detalles anidados.
#     """
#     queryset = Venta.objects.all().select_related('cliente', 'usuario', 'empresa').prefetch_related('detalles')
#     serializer_class = VentaSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     filter_backends = [filters.SearchFilter, DjangoFilterBackend]
#     search_fields = ['cliente__nombre', 'usuario__username', 'estado']
#     filterset_fields = ['empresa', 'estado', 'fecha', 'cliente']

#     def perform_create(self, serializer):
#         serializer.save()

#     def perform_update(self, serializer):
#         serializer.save()
