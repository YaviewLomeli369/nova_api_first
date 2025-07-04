from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from accounts.models import Rol
from accounts.serializers import RolSerializer

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]