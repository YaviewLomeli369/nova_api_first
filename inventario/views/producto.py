from rest_framework import viewsets
from inventario.models import Producto
from inventario.serializers import ProductoSerializer
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions

class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

    def get_queryset(self):
        user = self.request.user
        return Producto.objects.filter(empresa=user.empresa)



# from rest_framework import viewsets
# from inventario.models import Producto
# from inventario.serializers import ProductoSerializer
# from rest_framework.permissions import IsAuthenticated

# class ProductoViewSet(viewsets.ModelViewSet):
#     queryset = Producto.objects.all()
#     serializer_class = ProductoSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return self.queryset.filter(empresa=self.request.user.empresa)
