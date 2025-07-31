from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from reportes.services.stock_service import obtener_stock_actual_por_producto
from reportes.serializers.stock_serializer import StockActualProductoSerializer
from reportes.filters.stock_filter import StockActualFilter
from reportes.models import ReporteGenerado

class ReporteStockActualView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa = request.user.empresa_actual or request.user.empresa_set.first()

        # Leer filtros GET
        sucursal_id = request.query_params.get('sucursal')
        categoria_id = request.query_params.get('categoria')
        minimo_stock = request.query_params.get('minimo_stock', 'false').lower() == 'true'

        # Importar modelos para validación de filtros
        from core.models import Sucursal
        from inventario.models import Categoria

        sucursal = None
        if sucursal_id:
            try:
                sucursal = Sucursal.objects.get(pk=sucursal_id, empresa=empresa)
            except Sucursal.DoesNotExist:
                return Response({"error": "Sucursal no encontrada"}, status=400)

        categoria = None
        if categoria_id:
            try:
                categoria = Categoria.objects.get(pk=categoria_id, empresa=empresa)
            except Categoria.DoesNotExist:
                return Response({"error": "Categoría no encontrada"}, status=400)

        # Obtener datos
        queryset = obtener_stock_actual_por_producto(
            empresa=empresa,
            sucursal=sucursal,
            categoria_id=categoria.id if categoria else None,
            minimo_stock=minimo_stock
        )

        # Serializar
        serializer = StockActualProductoSerializer(queryset, many=True)

        # Guardar reporte generado
        filtros = {
            "sucursal": sucursal_id,
            "categoria": categoria_id,
            "minimo_stock": minimo_stock,
        }
        ReporteGenerado.objects.create(
            nombre="Stock actual por producto y categoría",
            tipo="INVENTARIO",
            estado="COMPLETO",
            filtros_usados=filtros,
            generado_por=request.user,
            empresa=empresa,
        )

        return Response(serializer.data)
