from rest_framework import viewsets
from inventario.models import Inventario
from inventario.serializers import InventarioSerializer
from rest_framework.permissions import IsAuthenticated

class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.select_related('producto', 'sucursal')
    serializer_class = InventarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(producto__empresa=self.request.user.empresa)
