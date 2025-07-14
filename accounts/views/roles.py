from rest_framework import viewsets
from accounts.models import Rol
from accounts.serializers.rol_serializers import RoleSerializer
from accounts.permissions import IsSuperAdmin  # Importa tu permiso personalizado

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsSuperAdmin]

# from rest_framework import viewsets
# from accounts.models import Rol
# from accounts.serializers.rol_serializers import RoleSerializer
# from accounts.permissions import IsSuperAdmin  # Asegúrate de importar desde donde lo tengas definido

# class RoleViewSet(viewsets.ModelViewSet):
#     queryset = Rol.objects.all()
#     serializer_class = RoleSerializer
#     permission_classes = [IsSuperAdmin]
