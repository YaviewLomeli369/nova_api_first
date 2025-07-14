from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import F

from inventario.models import Producto
from inventario.serializers import ProductoSerializer

from accounts.permissions import IsSuperAdminOrEmpresaAdmin, IsInventario

class StockAlertView(APIView):
    permission_classes = [IsAuthenticated & (IsSuperAdminOrEmpresaAdmin | IsInventario)]

    def get(self, request):
        empresa = request.user.empresa
        productos_alerta = Producto.objects.filter(
            empresa=empresa,
            activo=True,
            inventarios__cantidad__lt=F('stock_minimo')
        ).distinct()

        serializer = ProductoSerializer(productos_alerta, many=True)
        return Response(serializer.data)

# # inventario/views/stock_alerts.py

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from inventario.models import Producto
# from inventario.serializers import ProductoSerializer
# from django.db.models import F

# class StockAlertView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         empresa = request.user.empresa
#         productos_alerta = Producto.objects.filter(
#             empresa=empresa,
#             activo=True,
#             inventarios__cantidad__lt=F('stock_minimo')
#         ).distinct()

#         serializer = ProductoSerializer(productos_alerta, many=True)
#         return Response(serializer.data)
