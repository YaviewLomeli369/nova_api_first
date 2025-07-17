from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from compras.models import Compra
from compras.serializers import CompraSerializer
from accounts.permissions import IsSuperAdminOrCompras
from rest_framework import serializers


class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer
    # permission_classes = [IsSuperAdminOrCompras] # 👈 Asegúrate de tener este permiso
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'proveedor']
    # search_fields = ['factura', 'comentarios']
    search_fields = ['detalles__producto__nombre']

    # ordering_fields = [ 'creado_en']
    # ordering = []
    ordering_fields = ['fecha', 'total']
    ordering = ['-fecha']  # Orden descendente por defecto

    def get_queryset(self):
        usuario = self.request.user
        empresa = getattr(usuario, 'empresa', None)
        if empresa:
            return Compra.objects.filter(empresa=empresa)
        return Compra.objects.none()
    # def get_queryset(self):
    #     empresa = getattr(self.request.user, 'empresa_actual', None)
    #     if empresa:
    #         return Compra.objects.filter(empresa=empresa)
    #     return Compra.objects.none()

    # def perform_create(self, serializer):
    #     empresa = getattr(self.request.user, 'empresa_actual', None)
    #     serializer.save(empresa=empresa)
    def perform_create(self, serializer):
        usuario = self.request.user
        empresa = usuario.empresa
        if not getattr(usuario, 'sucursal_actual', None):
            raise serializers.ValidationError("El usuario no tiene una sucursal asignada.")
        serializer.save(empresa=empresa, usuario=usuario)
