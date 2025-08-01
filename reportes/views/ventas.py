from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from reportes.filters.reporte_filter import ReporteVentasFilter
from reportes.services.calculos_kpis import ventas_agrupadas_por_fecha
from reportes.serializers.kpi_serializer import VentaAgrupadaSerializer
from reportes.models import ReporteGenerado
from reportes.utils.filtros import serializar_filtros
from django.db.models import Sum, F
from reportes.services.ventas import calcular_promedio_ticket, obtener_productos_mas_vendidos
from reportes.serializers.ventas import PromedioTicketVentaSerializer, ProductoMasVendidoSerializer
from datetime import datetime, timedelta
from rest_framework import serializers
from ventas.models import DetalleVenta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F
from ventas.models import DetalleVenta
from datetime import datetime

class ProductosMasVendidosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        empresa = user.empresa_actual  # Asegura que estás usando empresa del usuario

        # Filtros
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        sucursal_id = request.query_params.get('sucursal_id')

        # Construimos filtros - siempre filtrar por empresa del usuario
        filtros = {
            'venta__empresa': empresa,
            'venta__estado': 'COMPLETADA',  # Solo ventas completadas
        }

        # Filtros de fecha
        if fecha_inicio:
            filtros['venta__fecha__date__gte'] = fecha_inicio
        if fecha_fin:
            filtros['venta__fecha__date__lte'] = fecha_fin

        # Filtro por sucursal usando el campo sucursal de la venta
        if sucursal_id:
            try:
                from core.models import Sucursal
                # Verificar que la sucursal pertenece a la empresa del usuario
                sucursal = Sucursal.objects.get(id=sucursal_id, empresa=empresa)
                # Filtrar por ventas de esa sucursal
                filtros['venta__sucursal'] = sucursal
            except Sucursal.DoesNotExist:
                # Si la sucursal no existe o no pertenece a la empresa, ignorar el filtro
                pass

        # Consulta agregada
        productos = (
            DetalleVenta.objects.filter(**filtros)
            .values(
                id_producto=F('producto__id'),
                nombre=F('producto__nombre'),
                codigo=F('producto__codigo'),
            )
            .annotate(total_vendido=Sum('cantidad'))
            .order_by('-total_vendido')
        )

        return Response(productos)



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