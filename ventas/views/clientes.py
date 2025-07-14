# ventas/views/clientes.py
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from ventas.models import Cliente
from ventas.serializers import ClienteSerializer
from ventas.filters.clientes import ClienteFilter  # 👈 Filtro avanzado para Clientes
from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsVendedor  # 👈 Permisos personalizados

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().select_related('empresa')
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated & (IsSuperAdmin | IsEmpresaAdmin | IsVendedor)]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'rfc', 'correo', 'telefono']
    filterset_class = ClienteFilter

    def get_queryset(self):
        user = self.request.user
        if user.rol.nombre == "Superadministrador":
            # Superadmin ve todos los clientes
            return self.queryset
        else:
            # Los demás solo clientes de su empresa
            return self.queryset.filter(empresa=user.empresa)
