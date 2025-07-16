from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from core.models import Empresa
from core.serializers import EmpresaSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsSuperAdminOrEmpresaAdmin
from core.filters import EmpresaFilter
class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminOrEmpresaAdmin]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmpresaFilter  # usa filtro custom
  
    search_fields = ['nombre', 'rfc', 'domicilio_fiscal', 'regimen_fiscal']
    ordering_fields = ['nombre', 'creado_en', 'actualizado_en']
    ordering = ['nombre']


    # Paginación si tienes configurada en settings.py o puedes definir aquí un PageNumberPagination personalizada
