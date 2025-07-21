# accounts/permissions.py

from rest_framework import permissions

class EsAdminEmpresa(permissions.BasePermission):
    """
    Permite solo a usuarios con rol administrador de la empresa.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.rol and request.user.rol.nombre == 'Administrador'
