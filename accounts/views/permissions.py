from django.contrib.auth.models import Permission
from rest_framework import viewsets
from rest_framework.permissions import BasePermission

from accounts.serializers.group_permission_serializers import PermissionSerializer


# 🔐 Permiso personalizado: Solo Superadmin o Auditor/Legal
class IsSuperAdminOrAuditor(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and 
            user.rol is not None and 
            user.rol.nombre in ["Superadministrador", "Auditor / Legal"]
        )


# 📋 Vista de solo lectura para listar permisos disponibles en el sistema
class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsSuperAdminOrAuditor]


