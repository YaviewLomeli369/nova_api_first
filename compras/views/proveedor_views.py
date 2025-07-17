# compras/views/proveedor_views.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from compras.models import Proveedor
from compras.serializers import ProveedorSerializer
from accounts.permissions import IsSuperAdminOrCompras
from rest_framework import serializers

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    # permission_classes = [IsSuperAdminOrCompras] # 👈 Asegúrate de tener este permiso
    permission_classes = [AllowAny]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'rfc', 'correo', 'telefono']
    search_fields = ['nombre', 'rfc', 'correo']
    ordering_fields = ['nombre', 'creado_en', 'actualizado_en']
    ordering = ['nombre']

    def get_queryset(self):
        user = self.request.user
        empresa = getattr(user, 'empresa_actual', None)
        if empresa:
            return Proveedor.objects.filter(empresa=empresa)
        return Proveedor.objects.none()

    def perform_create(self, serializer):
        empresa = getattr(self.request.user, 'empresa', None)
        print("Empresa actual del usuario:", empresa)
        if empresa is None:
            # Si no hay empresa, puedes lanzar excepción o manejar el error
            raise serializers.ValidationError("No se encontró empresa asignada al usuario")
        serializer.save(empresa=empresa)
