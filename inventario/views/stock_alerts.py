from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import F

from inventario.models import Producto
from inventario.serializers import ProductoSerializer

from accounts.permissions import IsSuperAdminOrEmpresaAdmin, IsInventario
from django.db.models import Sum

# inventario/views/stock_alerts.py (o donde prefieras)

from datetime import date, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# from inventario.models import Batch
from inventario.serializers import BatchSerializer

from accounts.permissions import IsSuperAdminOrEmpresaAdmin, IsInventario

class ExpirationAlertView(APIView):
    permission_classes = [IsAuthenticated & (IsSuperAdminOrEmpresaAdmin | IsInventario)]

    def get(self, request):
        empresa = request.user.empresa
        hoy = date.today()
        alerta_hasta = hoy + timedelta(days=30)  # Próximos 30 días

        lotes_proximos_a_vencer = Batch.objects.filter(
            empresa=empresa,
            activo=True,
            fecha_vencimiento__lte=alerta_hasta,
            fecha_vencimiento__gte=hoy
        ).order_by('fecha_vencimiento')

        serializer = BatchSerializer(lotes_proximos_a_vencer, many=True)
        return Response(serializer.data)

class StockAlertView(APIView):
    permission_classes = [IsAuthenticated & (IsSuperAdminOrEmpresaAdmin | IsInventario)]

    def get(self, request):
        empresa = request.user.empresa
        productos_alerta = Producto.objects.filter(
            empresa=empresa,
            activo=True
        ).annotate(
            stock_total=Sum('inventarios__cantidad')
        ).filter(
            stock_total__lt=F('stock_minimo')
        )

        serializer = ProductoSerializer(productos_alerta, many=True)
        return Response(serializer.data)



# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.db.models import F

# from inventario.models import Producto
# from inventario.serializers import ProductoSerializer

# from accounts.permissions import IsSuperAdminOrEmpresaAdmin, IsInventario

# class StockAlertView(APIView):
#     permission_classes = [IsAuthenticated & (IsSuperAdminOrEmpresaAdmin | IsInventario)]

#     def get(self, request):
#         empresa = request.user.empresa
#         productos_alerta = Producto.objects.filter(
#             empresa=empresa,
#             activo=True,
#             inventarios__cantidad__lt=F('stock_minimo')
#         ).distinct()

#         serializer = ProductoSerializer(productos_alerta, many=True)
#         return Response(serializer.data)
