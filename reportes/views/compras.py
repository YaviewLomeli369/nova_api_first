from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Sum, Count

from compras.models import Compra
from reportes.serializers.compras_serializer import ReporteComprasProveedorSerializer
from reportes.filters.reporte_compras_filter import ReporteComprasFilter
from reportes.models import ReporteGenerado
from django_filters.rest_framework import DjangoFilterBackend

class ReporteComprasProveedorView(GenericAPIView):  # <- CORRECTO
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReporteComprasFilter
    queryset = Compra.objects.all()  # Necesario para que filter_queryset funcione

    def get(self, request):
        # Aplica los filtros
        queryset = self.filter_queryset(self.get_queryset())

        resultado = (
            queryset
            .values('proveedor__id', 'proveedor__nombre')
            .annotate(
                total_compras=Sum('total'),
                num_compras=Count('id')
            )
            .order_by('-total_compras')
        )

        # Guardar el reporte
        filtros = request.query_params.dict()
        ReporteGenerado.objects.create(
            nombre="Reporte de compras por proveedor",
            tipo='COMPRAS',
            estado='COMPLETO',
            filtros_usados=filtros,
            generado_por=request.user,
            empresa=getattr(request.user, 'empresa_actual', None) or request.user.empresa_set.first()
        )

        serializer = ReporteComprasProveedorSerializer(resultado, many=True)
        return Response(serializer.data)
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from reportes.services.compras_service import reporte_compras_por_proveedor
# from reportes.serializers.compras_serializer import ReporteComprasProveedorSerializer
# from reportes.models import ReporteGenerado
# from django.utils import timezone

# from rest_framework.generics import GenericAPIView
# from django_filters.rest_framework import DjangoFilterBackend
# from reportes.filters.reporte_compras_filter import ReporteComprasFilter

# from django.db.models import Sum, Count  # Para agregaciones

# from compras.models import Compra  # Modelo base para el queryset
# from django_filters.rest_framework import DjangoFilterBackend  # Para filtros automáticos

# class ReporteComprasProveedorView(APIView):
#     permission_classes = [IsAuthenticated]
#     filter_backends = [DjangoFilterBackend]
#     filterset_class = ReporteComprasFilter


#     def get(self, request):
#         # Aplica filtros usando el sistema integrado
#         queryset = self.filter_queryset(Compra.objects.all())

#         resultado = (
#             queryset
#             .values('proveedor__id', 'proveedor__nombre')
#             .annotate(
#                 total_compras=Sum('total'),
#                 num_compras=Count('id')
#             )
#             .order_by('-total_compras')
#         )

#         # Guardar reporte generado
#         filtros = request.query_params.dict()
#         ReporteGenerado.objects.create(
#             nombre="Reporte de compras por proveedor",
#             tipo='COMPRAS',
#             estado='COMPLETO',
#             filtros_usados=filtros,
#             generado_por=request.user,
#             empresa=getattr(request.user, 'empresa_actual', None) or request.user.empresa_set.first()
#         )

#         serializer = ReporteComprasProveedorSerializer(resultado, many=True)
#         return Response(serializer.data)
#     # def get(self, request):
#     #     fecha_inicio = request.query_params.get('fecha_inicio')
#     #     fecha_fin = request.query_params.get('fecha_fin')
#     #     proveedor_id = request.query_params.get('proveedor')

#     #     # Lógica de negocio
#     #     data = reporte_compras_por_proveedor(fecha_inicio, fecha_fin, proveedor_id)

#     #     # Guardar reporte generado con estado COMPLETO porque la consulta fue sincrónica
#     #     filtros = {
#     #         'fecha_inicio': fecha_inicio,
#     #         'fecha_fin': fecha_fin,
#     #         'proveedor': proveedor_id,
#     #     }

#     #     reporte = ReporteGenerado.objects.create(
#     #         nombre="Reporte de compras por proveedor",
#     #         tipo='COMPRAS',
#     #         estado='COMPLETO',
#     #         filtros_usados=filtros,
#     #         generado_por=request.user,
#     #         empresa=getattr(request.user, 'empresa_actual', None) or request.user.empresa_set.first()
#     #     )

#     #     serializer = ReporteComprasProveedorSerializer(data, many=True)
#     #     return Response(serializer.data)
