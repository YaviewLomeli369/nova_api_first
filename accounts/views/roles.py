from rest_framework import viewsets
from accounts.models import Rol
from accounts.serializers.rol_serializers import RoleSerializer
from accounts.permissions import IsSuperAdmin , IsSuperAdminOrEmpresaAdmin # Importa tu permiso personalizado

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsSuperAdminOrEmpresaAdmin]

