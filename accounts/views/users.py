from rest_framework import viewsets, filters
from accounts.models import Usuario
from accounts.serializers.user_serializers import UsuarioCreateSerializer, UsuarioDetailSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied

from accounts.permissions import IsSuperAdminOrEmpresaAdmin  # permiso combinado importado

class UsuarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperAdminOrEmpresaAdmin]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['username', 'email']
    filterset_fields = ['activo', 'empresa', 'rol']

    def get_queryset(self):
        user = self.request.user

        if user.rol.nombre == "Superadministrador":
            return Usuario.objects.select_related('empresa', 'rol').all()
        elif user.rol.nombre == "Administrador de Empresa":
            return Usuario.objects.select_related('empresa', 'rol').filter(empresa=user.empresa)
        else:
            raise PermissionDenied("No tienes permisos para ver usuarios")

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioDetailSerializer

    def perform_create(self, serializer):
        user = self.request.user

        if user.rol.nombre == "Superadministrador":
            serializer.save()
        elif user.rol.nombre == "Administrador de Empresa":
            serializer.save(empresa=user.empresa)
        else:
            raise PermissionDenied("No puedes crear usuarios")

    def perform_destroy(self, instance):
        # Baja lógica: no se borra, solo se inactiva
        instance.activo = False
        instance.save()



