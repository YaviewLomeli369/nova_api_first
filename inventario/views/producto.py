from rest_framework import viewsets
from inventario.models import Producto
from inventario.serializers import ProductoSerializer
from rest_framework.permissions import IsAuthenticated

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(empresa=self.request.user.empresa)
