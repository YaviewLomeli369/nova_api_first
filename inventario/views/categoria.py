from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from inventario.models import Categoria
from inventario.serializers import CategoriaSerializer

from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

    def get_queryset(self):
        # Multitenencia: cada usuario solo ve categorías de su empresa
        user = self.request.user
        return self.queryset.filter(empresa=user.empresa)


# from rest_framework import viewsets
# from inventario.models import Categoria
# from inventario.serializers import CategoriaSerializer
# from rest_framework.permissions import IsAuthenticated

# class CategoriaViewSet(viewsets.ModelViewSet):
#     queryset = Categoria.objects.all()
#     serializer_class = CategoriaSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return self.queryset.filter(empresa=self.request.user.empresa)
