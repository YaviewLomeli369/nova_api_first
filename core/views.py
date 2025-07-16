from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from core.models import Empresa, Sucursal
from core.serializers import EmpresaSerializer, SucursalSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsSuperAdminOrEmpresaAdmin
from core.filters import EmpresaFilter, SucursalFilter
class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminOrEmpresaAdmin]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmpresaFilter  # usa filtro custom
  
    search_fields = ['nombre', 'rfc', 'domicilio_fiscal', 'regimen_fiscal']
    ordering_fields = ['nombre', 'creado_en', 'actualizado_en']
    ordering = ['nombre']




class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminOrEmpresaAdmin]
    filterset_class = SucursalFilter

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa']
    search_fields = ['nombre', 'direccion']
    ordering_fields = ['nombre', 'creado_en']
    ordering = ['nombre']