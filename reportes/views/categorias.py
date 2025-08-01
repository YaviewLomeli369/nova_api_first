from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from rest_framework import status
from reportes.serializers.categorias import CategoriaRentableSerializer
from reportes.services.categorias import categorias_mas_rentables

class CategoriasMasRentablesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        empresa = getattr(user, 'empresa', None)
        if empresa is None:
            return Response({"detail": "Usuario no tiene empresa asignada."}, status=status.HTTP_400_BAD_REQUEST)

        # Parámetros
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        sucursal_id = request.query_params.get('sucursal_id')
        pagina = request.query_params.get('pagina', '1')
        items_por_pagina = request.query_params.get('items_por_pagina', '10')

        try:
            pagina = max(1, int(pagina))
            items_por_pagina = max(1, int(items_por_pagina))
        except ValueError:
            return Response({"detail": "Parámetros de paginación inválidos."}, status=status.HTTP_400_BAD_REQUEST)

        if fecha_inicio:
            fecha_inicio = parse_date(fecha_inicio)
        if fecha_fin:
            fecha_fin = parse_date(fecha_fin)

        resultado = categorias_mas_rentables(
            empresa=empresa,
            sucursal_id=sucursal_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            pagina=pagina,
            items_por_pagina=items_por_pagina
        )

        serializer = CategoriaRentableSerializer(resultado['resultados'], many=True)
        return Response({
            'total': resultado['total'],
            'pagina': resultado['pagina'],
            'items_por_pagina': resultado['items_por_pagina'],
            'categorias': serializer.data
        })
