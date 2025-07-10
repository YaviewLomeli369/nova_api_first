from rest_framework import viewsets
from inventario.models import Categoria
from inventario.serializers import CategoriaSerializer
from rest_framework.permissions import IsAuthenticated

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(empresa=self.request.user.empresa)
