from rest_framework import viewsets
from accounts.models import Rol
from accounts.serializers import RolSerializer
from rest_framework.permissions import IsAuthenticated

class RolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]
