from rest_framework import viewsets, permissions
from accounts.models import Rol
from accounts.serializers.rol_serializers import RolSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Puedes agregar filtros o permisos especiales aquí

# from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated
# from accounts.models import Rol
# from accounts.serializers.rol_serializers import RolSerializer

# from rest_framework import serializers

# # from rest_framework import viewsets
# # from rest_framework.permissions import IsAuthenticated
# # from accounts.models import Rol
# # from accounts.serializers import RolSerializer

# class RolViewSet(viewsets.ModelViewSet):
#     queryset = Rol.objects.all()
#     serializer_class = RolSerializer
#     permission_classes = [IsAuthenticated]