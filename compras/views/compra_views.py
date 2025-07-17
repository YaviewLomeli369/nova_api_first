from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from compras.models import Compra
from compras.serializers import CompraSerializer
from accounts.permissions import IsSuperAdminOrCompras



class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer
    # permission_classes = [IsSuperAdminOrCompras] # 👈 Asegúrate de tener este permiso
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'proveedor']
    search_fields = ['factura', 'comentarios']
    ordering_fields = [ 'creado_en']
    ordering = []

    def get_queryset(self):
        empresa = getattr(self.request.user, 'empresa_actual', None)
        if empresa:
            return Compra.objects.filter(empresa=empresa)
        return Compra.objects.none()

    def perform_create(self, serializer):
        empresa = getattr(self.request.user, 'empresa_actual', None)
        serializer.save(empresa=empresa)
