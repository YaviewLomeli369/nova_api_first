# views/eficiencia_compras.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from reportes.filters.eficiencia_compras import EficienciaComprasFilter
from reportes.services.eficiencia_compras import calcular_eficiencia_compras
from reportes.serializers.eficiencia_compras import EficienciaComprasSerializer

class EficienciaComprasView(APIView):
    permission_classes = [IsAuthenticated]
    filterset_class = EficienciaComprasFilter

    def get(self, request, *args, **kwargs):
        # Filtrar parámetros de consulta
        empresa = request.query_params.get('empresa')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        if not empresa or not fecha_inicio or not fecha_fin:
            return Response(
                {"detail": "Parámetros 'empresa', 'fecha_inicio' y 'fecha_fin' son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            resultado = calcular_eficiencia_compras(empresa, fecha_inicio, fecha_fin)
            serializer = EficienciaComprasSerializer(resultado)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# # views/eficiencia_compras.py
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# # from utils.permissions import TienePermisoEmpresa
# from reportes.services.eficiencia_compras import calcular_eficiencia_compras
# from reportes.serializers.eficiencia_compras import EficienciaComprasSerializer

# class EficienciaComprasView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         empresa_id = request.query_params.get("empresa")
#         fecha_inicio = request.query_params.get("fecha_inicio")
#         fecha_fin = request.query_params.get("fecha_fin")

#         if not empresa_id or not fecha_inicio or not fecha_fin:
#             return Response({"error": "Parámetros requeridos: empresa, fecha_inicio, fecha_fin"}, status=400)

#         datos = calcular_eficiencia_compras(empresa_id, fecha_inicio, fecha_fin)
#         serializer = EficienciaComprasSerializer(datos)
#         return Response(serializer.data)
