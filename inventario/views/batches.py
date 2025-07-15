from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from inventario.models import Inventario
from inventario.serializers import InventarioSerializer, BatchSerializer
from django.utils import timezone

from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions
from datetime import timedelta

class BatchView(APIView):
    permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

    def get(self, request):
        user = request.user
        hoy = timezone.now().date()
        alerta_hasta = hoy + timedelta(days=30)

        inventarios = Inventario.objects.select_related('producto').filter(
            producto__empresa=user.empresa,
            fecha_vencimiento__isnull=False,
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=alerta_hasta
        ).order_by('fecha_vencimiento')

        serializer = BatchSerializer(inventarios, many=True)
        return Response(serializer.data)






# # inventario/views/batches.py

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from inventario.models import Inventario
# from inventario.serializers import InventarioSerializer
# from django.utils import timezone

# class BatchView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         empresa = request.user.empresa
#         hoy = timezone.now().date()
#         inventarios = Inventario.objects.filter(
#             producto__empresa=empresa,
#             fecha_vencimiento__isnull=False
#         ).order_by('fecha_vencimiento')

#         serializer = InventarioSerializer(inventarios, many=True)
#         return Response(serializer.data)
