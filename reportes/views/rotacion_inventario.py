from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from reportes.services.rotacion_inventario import calcular_rotacion_inventario
from reportes.serializers.rotacion_inventario import RotacionInventarioSerializer
from reportes.filters.rotacion_inventario import RotacionInventarioFilter
from core.models import Empresa, Sucursal
from rest_framework import status
from rest_framework.permissions import AllowAny

class RotacionInventarioView(APIView):
    permission_classes = [AllowAny]  # Ajusta roles en tu permiso

    def get(self, request):
        # 1. Aplicar filtro manualmente (django_filters no funciona directo con APIView)
        filtro = RotacionInventarioFilter(request.GET)

        if not filtro.is_valid():
            return Response({"error": "Parámetros inválidos", "detalles": filtro.errors}, status=status.HTTP_400_BAD_REQUEST)

        empresa = filtro.form.cleaned_data['empresa']
        sucursal = filtro.form.cleaned_data.get('sucursal')  # Opcional
        fecha_inicio = filtro.form.cleaned_data['fecha_inicio']
        fecha_fin = filtro.form.cleaned_data['fecha_fin']

        # 2. Llamar función servicio con parámetros
        resultado = calcular_rotacion_inventario(empresa.id, fecha_inicio, fecha_fin)

        # 3. Serializar resultado
        serializer = RotacionInventarioSerializer(resultado)

        return Response(serializer.data, status=status.HTTP_200_OK)



# # reportes/views/rotacion_inventario.py

# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.response import Response

# from reportes.services.rotacion_inventario import calcular_rotacion_inventario
# from reportes.serializers.rotacion_inventario import RotacionInventarioFiltroSerializer, RotacionInventarioResponseSerializer

# class RotacionInventarioPagination(PageNumberPagination):
#     page_size = 10

#     def get_paginated_response(self, data, totales=None, extra=None):
#         response = {
#             'count': self.page.paginator.count,
#             'next': self.get_next_link(),
#             'previous': self.get_previous_link(),
#             'results': data,
#             'totales': totales or {}
#         }
#         if extra:
#             response.update(extra)
#         return Response(response)

# class RotacionInventarioView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         data = request.query_params.copy()

#         # Sobrescribir o asegurar que la empresa siempre sea la del usuario autenticado
#         data['empresa_id'] = request.user.empresa.id

#         serializer = RotacionInventarioFiltroSerializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         filtros = serializer.validated_data

#         resultado = calcular_rotacion_inventario(**filtros)

#         paginator = RotacionInventarioPagination()
#         paginated = paginator.paginate_queryset(resultado['results'], request)

#         return paginator.get_paginated_response(
#             paginated,
#             totales=resultado['totales'],
#             extra={
#                 "agrupacion": filtros.get('agrupacion', 'mensual'),
#                 "fecha_inicio": filtros.get('fecha_inicio'),
#                 "fecha_fin": filtros.get('fecha_fin'),
#             }
#         )