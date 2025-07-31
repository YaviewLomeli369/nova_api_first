
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from inventario.models import MovimientoInventario
from inventario.serializers import MovimientoInventarioSerializer

class MovimientosRecientesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Devuelve los últimos 20 movimientos de inventario para debug
        """
        empresa = request.user.empresa_actual or request.user.empresa_set.first()
        
        movimientos = MovimientoInventario.objects.filter(
            inventario__producto__empresa=empresa
        ).select_related(
            'inventario__producto',
            'inventario__sucursal',
            'usuario'
        ).order_by('-fecha')[:20]
        
        serializer = MovimientoInventarioSerializer(movimientos, many=True)
        return Response(serializer.data)
