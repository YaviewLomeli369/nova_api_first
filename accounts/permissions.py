# accounts/permissions.py

from rest_framework.permissions import BasePermission
from accounts.constants import Roles


class IsEmpleado(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.rol and
            request.user.rol.nombre == "Empleado"
        )

# 🔐 Permisos base por rol exacto (uno por clase)
class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.SUPERADMIN

class IsEmpresaAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.ADMIN_EMPRESA

class IsVendedor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.VENDEDOR

class IsInventario(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.INVENTARIO

class IsCompras(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.COMPRAS

class IsContador(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.CONTADOR

class IsTesorero(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.TESORERO

class IsRecursosHumanos(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.RH

class IsAuditor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.AUDITOR

class IsClienteExterno(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre == Roles.CLIENTE


# 🔁 Combinaciones comunes (útiles para reutilizar en muchas vistas)

class IsSuperAdminOrEmpresaAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.SUPERADMIN, Roles.ADMIN_EMPRESA
        ]

class IsSuperAdminOrVendedor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.SUPERADMIN, Roles.VENDEDOR
        ]

class IsSuperAdminOrInventario(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.SUPERADMIN, Roles.INVENTARIO
        ]

class IsSuperAdminOrCompras(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.SUPERADMIN, Roles.COMPRAS
        ]

class IsSuperAdminOrContador(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.SUPERADMIN, Roles.CONTADOR
        ]

class IsSuperAdminOrTesorero(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.SUPERADMIN, Roles.TESORERO
        ]

class IsSuperAdminOrRecursosHumanos(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.SUPERADMIN, Roles.RH
        ]

class IsSuperAdminOrAuditor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.SUPERADMIN, Roles.AUDITOR
        ]

class IsEmpresaAdminOrVendedor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol.nombre in [
            Roles.ADMIN_EMPRESA, Roles.VENDEDOR
        ]


# 🔀 Helper dinámico para múltiples combinaciones OR
def OrPermissions(*perms):
    class _OrPermission(BasePermission):
        def has_permission(self, request, view):
            return any(perm().has_permission(request, view) for perm in perms)
    return _OrPermission


# 🛡️ Permisos basados en codename de Django (add_modelo, view_modelo, etc.)
def CustomPermission(permiso_codename):
    class _CustomPermission(BasePermission):
        def has_permission(self, request, view):
            return request.user.is_authenticated and request.user.has_perm(permiso_codename)
    return _CustomPermission
