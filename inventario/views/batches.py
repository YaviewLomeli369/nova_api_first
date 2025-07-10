# inventario/views/batches.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from inventario.models import Inventario
from inventario.serializers import InventarioSerializer
from django.utils import timezone

class BatchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa = request.user.empresa
        hoy = timezone.now().date()
        inventarios = Inventario.objects.filter(
            producto__empresa=empresa,
            fecha_vencimiento__isnull=False
        ).order_by('fecha_vencimiento')

        serializer = InventarioSerializer(inventarios, many=True)
        return Response(serializer.data)
