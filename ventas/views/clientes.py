# ventas/views/clientes.py
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from ventas.models import Cliente
from ventas.serializers import ClienteSerializer
from ventas.filters.clientes import ClienteFilter  # 👈 Importar el filtro avanzado

class ClienteViewSet(viewsets.ModelViewSet):
    """
    CRUD completo con búsqueda y filtro avanzado para Clientes
    """
    queryset = Cliente.objects.all().select_related('empresa')
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'rfc', 'correo', 'telefono']
    filterset_class = ClienteFilter  # 👈 Aquí usas el filtro avanzado


