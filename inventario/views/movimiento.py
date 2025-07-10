# inventario/views/movimiento.py

from rest_framework import viewsets
from inventario.models import MovimientoInventario
from inventario.serializers import MovimientoInventarioSerializer

class MovimientoInventarioViewSet(viewsets.ModelViewSet):  # ✅ debe ser ModelViewSet
    queryset = MovimientoInventario.objects.all()
    serializer_class = MovimientoInventarioSerializer
