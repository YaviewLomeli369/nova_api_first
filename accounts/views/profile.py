from rest_framework import generics
from rest_framework.permissions import BasePermission
from accounts.serializers.user_serializers import UsuarioSerializer

# Importa tus permisos personalizados si los quieres usar aparte (aquí no son usados directamente)
from accounts.permissions import (
    IsSuperAdmin,
    IsEmpresaAdmin,
    IsVendedor,
    IsInventario,
    IsCompras,
    IsContador,
    IsTesorero,
    IsRecursosHumanos,
    IsAuditor,
    IsClienteExterno,
)

# ✅ Permiso combinado para usuarios con cualquier rol válido en el sistema
class HasValidRole(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.rol and
            request.user.rol.nombre in [
                "Superadministrador",
                "Administrador de Empresa",
                "Vendedor",
                "Almacén / Inventario",
                "Compras / Proveedores",
                "Contador",
                "Tesorero / Finanzas",
                "Recursos Humanos",
                "Auditor / Legal",
                "Cliente externo"
            ]
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [HasValidRole]

    def get_object(self):
        return self.request.user

# from rest_framework import generics
# from rest_framework.permissions import BasePermission
# from accounts.serializers.user_serializers import UsuarioSerializer
# from accounts.permissions import (
#     IsSuperAdmin,
#     IsEmpresaAdmin,
#     IsVendedor,
#     IsInventario,
#     IsCompras,
#     IsContador,
#     IsTesorero,
#     IsRecursosHumanos,
#     IsAuditor,
#     IsClienteExterno,
# )

# # ✅ Permiso combinado para usuarios con cualquier rol válido en el sistema
# class HasValidRole(BasePermission):
#     def has_permission(self, request, view):
#         return (
#             request.user.is_authenticated and
#             request.user.rol and
#             request.user.rol.nombre in [
#                 "Superadministrador",
#                 "Administrador de Empresa",
#                 "Vendedor",
#                 "Almacén / Inventario",
#                 "Compras / Proveedores",
#                 "Contador",
#                 "Tesorero / Finanzas",
#                 "Recursos Humanos",
#                 "Auditor / Legal",
#                 "Cliente externo"
#             ]
#         )

# class ProfileView(generics.RetrieveUpdateAPIView):
#     serializer_class = UsuarioSerializer
#     permission_classes = [HasValidRole]

#     def get_object(self):
#         return self.request.user
