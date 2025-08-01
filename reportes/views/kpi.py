from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from reportes.services.kpi import obtener_rentabilidad_por_producto_y_cliente
from reportes.serializers.kpi import RentabilidadProductoClienteSerializer
from datetime import datetime, timedelta

class RentabilidadProductoClienteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa_id = request.user.empresa_actual.id

        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        cliente_id = request.query_params.get('cliente_id')
        producto_id = request.query_params.get('producto_id')

        try:
            if fecha_inicio:
                fecha_inicio = datetime.fromisoformat(fecha_inicio).date()
            if fecha_fin:
                fecha_fin = datetime.fromisoformat(fecha_fin).date()
        except ValueError:
            return Response({"error": "Formato de fecha inválido, usar YYYY-MM-DD"}, status=400)

        # Sumar un día para hacer fecha_fin exclusivo y que incluya todo el día final
        fecha_fin_exclusiva = fecha_fin + timedelta(days=1) if fecha_fin else None

        data = obtener_rentabilidad_por_producto_y_cliente(
            empresa_id=empresa_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin_exclusiva,
            cliente_id=cliente_id,
            producto_id=producto_id
        )

        serializer = RentabilidadProductoClienteSerializer(data, many=True)
        return Response(serializer.data)