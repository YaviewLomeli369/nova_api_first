# reportes/views/reportes_compras.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from reportes.services.reportes_compras import obtener_dias_promedio_pago_proveedores
from reportes.serializers.reportes_compras import DiasPromedioPagoProveedorSerializer

class DiasPromedioPagoProveedorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa = request.user.empresa_actual
        data = obtener_dias_promedio_pago_proveedores(empresa)
        serializer = DiasPromedioPagoProveedorSerializer(data, many=True)
        return Response(serializer.data)
