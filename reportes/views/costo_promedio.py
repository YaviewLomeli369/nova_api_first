# reportes/views/costo_promedio.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from reportes.services.costo_promedio import calcular_cppp
from reportes.serializers.costo_promedio import CostoPromedioPonderadoSerializer
from reportes.filters.costo_promedio import CostoPromedioFilter

class CostoPromedioPonderadoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Filtros desde query params
        producto_id = request.query_params.get("producto")
        empresa_id = request.user.empresa.id  # Se asume multitenencia

        if not producto_id:
            return Response({"detail": "Se requiere el parámetro 'producto'."}, status=400)

        # Filtros opcionales
        proveedor_id = request.query_params.get("proveedor")
        fecha_inicio = request.query_params.get("fecha_inicio")
        fecha_fin = request.query_params.get("fecha_fin")

        # Ejecutar cálculo
        data = calcular_cppp(
            producto_id=int(producto_id),
            empresa_id=empresa_id,
            proveedor_id=int(proveedor_id) if proveedor_id else None,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

        # Serializar resultado
        serializer = CostoPromedioPonderadoSerializer(data)
        return Response(serializer.data)
