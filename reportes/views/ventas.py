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
from reportes.services.ventas import calcular_promedio_ticket
from reportes.serializers.ventas import PromedioTicketVentaSerializer

from datetime import datetime, timedelta


class PromedioTicketVentaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa_id = request.user.empresa_actual.id

        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        try:
            if fecha_inicio:
                fecha_inicio = datetime.fromisoformat(fecha_inicio)
            if fecha_fin:
                # Se suma 1 día para incluir todo el día seleccionado
                fecha_fin = datetime.fromisoformat(fecha_fin) + timedelta(days=1)
        except ValueError:
            return Response({"error": "Formato de fecha inválido. Usa YYYY-MM-DD"}, status=400)

        data = calcular_promedio_ticket(
            empresa_id=empresa_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        serializer = PromedioTicketVentaSerializer(data)
        return Response(serializer.data)


class ReporteVentasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filtro = ReporteVentasFilter(data=request.query_params)
        filtro.is_valid(raise_exception=True)
        empresa = request.user.empresa

        # Sumamos 1 día a fecha_fin para incluir completamente el último día
        fecha_inicio = filtro.validated_data['fecha_inicio']
        fecha_fin = filtro.validated_data['fecha_fin'] + timedelta(days=1)

        datos_ventas = ventas_agrupadas_por_fecha(
            empresa=empresa,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            agrupacion=filtro.validated_data['agrupacion']
        )

        serializer = VentaAgrupadaSerializer(datos_ventas, many=True, agrupacion=filtro.validated_data['agrupacion'])

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