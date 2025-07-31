from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from reportes.filters.reporte_filter import ReporteVentasFilter
from reportes.services.calculos_kpis import ventas_agrupadas_por_fecha
from reportes.serializers.kpi_serializer import VentaAgrupadaSerializer
from reportes.models import ReporteGenerado
from reportes.utils.filtros import serializar_filtros
from django.db.models.functions import TruncDate, TruncMonth, TruncDay
from django.db.models import Sum

class ReporteVentasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filtro = ReporteVentasFilter(data=request.query_params)
        filtro.is_valid(raise_exception=True)
        empresa = request.user.empresa # Ajusta según tu modelo de usuario
        # empresa_actual = request.user.empresa 

        datos_ventas = ventas_agrupadas_por_fecha(
            empresa=empresa,
            fecha_inicio=filtro.validated_data['fecha_inicio'],
            fecha_fin=filtro.validated_data['fecha_fin'],
            agrupacion=filtro.validated_data['agrupacion']
        )

        # serializer = VentaAgrupadaSerializer(datos_ventas, many=True)
        serializer = VentaAgrupadaSerializer(datos_ventas, many=True, agrupacion=filtro.validated_data['agrupacion'])

        # Convertir los filtros a tipos serializables (string)
        filtros_serializables = serializar_filtros(filtro.validated_data)

        ReporteGenerado.objects.create(
            nombre=f"Reporte de ventas agrupado por {filtro.validated_data['agrupacion']}",
            tipo="VENTAS",
            estado="COMPLETO",
            filtros_usados=filtros_serializables,
            generado_por=request.user,
            empresa=empresa
        )

        return Response(serializer.data)
