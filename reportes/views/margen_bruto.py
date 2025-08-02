from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from reportes.services.margen_bruto import calcular_margen_bruto

class MargenBrutoReporteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Datos base del usuario autenticado
        empresa_id = request.user.empresa.id

        # Filtros desde la URL
        sucursal_id = request.query_params.get('sucursal_id')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        agrupacion = request.query_params.get('agrupacion', 'mensual')  # mensual, diario, etc.

        # Calcular datos del reporte
        datos = calcular_margen_bruto(
            empresa_id=empresa_id,
            sucursal_id=sucursal_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            agrupacion=agrupacion
        )

        # Estructura lista para frontend: tabla, gráfica, o exportación
        return Response({
            "count": len(datos["detalle"]),
            "results": datos["detalle"],  # Lista por periodo con ventas, costos, margen
            "totales": datos["totales"],  # Acumulados globales
            "agrupacion": agrupacion,     # Para saber si agrupar por mes, día, etc.
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        })
