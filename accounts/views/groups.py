# 🧩 Django
from django.contrib.auth.models import Group

# 🛠️ Django REST Framework
from rest_framework import viewsets

# 📦 Serializers
from accounts.serializers.group_permission_serializers import GroupSerializer

# 🔐 Permisos personalizados
from accounts.permissions import IsSuperAdmin, CustomPermission


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Solo SuperAdmin puede modificar grupos
            return [IsSuperAdmin()]
        elif self.action in ['list', 'retrieve']:
            # Ver grupos requiere permiso explícito de Django
            return [CustomPermission('auth.view_group')()]
        # Fallback seguro
        return [IsSuperAdmin()]

# from django.contrib.auth.models import Group
# from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated

# from accounts.serializers.group_permission_serializers import GroupSerializer

# class GroupViewSet(viewsets.ModelViewSet):
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer
#     permission_classes = [IsAuthenticated]  # O usa tu CustomPermission
