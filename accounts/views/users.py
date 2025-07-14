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




# from rest_framework import viewsets, permissions, filters
# from accounts.models import Usuario
# from accounts.serializers.user_serializers import UsuarioCreateSerializer, UsuarioDetailSerializer
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.exceptions import PermissionDenied
# from rest_framework.permissions import IsAdminUser, BasePermission

# class IsSuperuserOrAdminRole(BasePermission):
#     def has_permission(self, request, view):
#         return bool(
#             request.user and request.user.is_authenticated and (
#                 request.user.is_superuser or
#                 (request.user.rol and request.user.rol.nombre.lower() == 'administrador')
#             )
#         )

# class UsuarioViewSet(viewsets.ModelViewSet):
#     # permission_classes = [permissions.IsAuthenticated]
#     # permission_classes = [IsAdminUser]
#     permission_classes = [IsSuperuserOrAdminRole]
#     filter_backends = [filters.SearchFilter, DjangoFilterBackend]
#     search_fields = ['username', 'email']
#     filterset_fields = ['activo', 'empresa', 'rol']

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_superuser:
#             return Usuario.objects.select_related('empresa', 'rol').all()
#         return Usuario.objects.filter(empresa=user.empresa)

#     def get_serializer_class(self):
#         if self.action == 'create':
#             return UsuarioCreateSerializer
#         return UsuarioDetailSerializer

#     def perform_create(self, serializer):
#         user = self.request.user
#         if not user.is_superuser:
#             # Solo admin puede crear usuarios fuera de su empresa
#             serializer.save(empresa=user.empresa)
#         else:
#             serializer.save()

#     def perform_destroy(self, instance):
#         instance.activo = False
#         instance.save()
