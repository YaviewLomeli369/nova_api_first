from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from ventas.models import Venta
from compras.models import Compra
from reportes.serializers.flujo_caja import FlujoCajaInputSerializer, FlujoCajaOutputSerializer

class FlujoCajaReporteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Validación de entrada
        input_serializer = FlujoCajaInputSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        fecha_inicio = data.get("fecha_inicio", timezone.now().replace(day=1).date())
        fecha_fin = data.get("fecha_fin", timezone.now().date())

        user = request.user
        empresa = user.empresa
        
        ventas_qs = Venta.objects.filter(
            fecha__range=(fecha_inicio, fecha_fin),
            empresa=empresa,
            # sucursal=sucursal,  <-- eliminar esta línea
        )

        compras_qs = Compra.objects.filter(
            fecha__range=(fecha_inicio, fecha_fin),
            empresa=empresa,
            # sucursal=sucursal,  <-- eliminar esta línea
        )

        total_ventas = ventas_qs.aggregate(total=Sum("total"))["total"] or 0
        total_compras = compras_qs.aggregate(total=Sum("total"))["total"] or 0
        utilidad_bruta = total_ventas - total_compras

        output_data = {
            "ingresos": float(total_ventas),
            "egresos": float(total_compras),
            "utilidad_bruta": float(utilidad_bruta),
            "moneda": "MXN",
            "filtros": {
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": fecha_fin.isoformat()
            }
        }

        output_serializer = FlujoCajaOutputSerializer(output_data)
        return Response(output_serializer.data)


# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from django.db.models import Sum
# from django.utils import timezone
# from datetime import datetime
# from ventas.models import Venta
# from compras.models import Compra

# class FlujoCajaReporteView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         fecha_inicio_str = request.query_params.get("fecha_inicio")
#         fecha_fin_str = request.query_params.get("fecha_fin")

#         try:
#             fecha_inicio = datetime.fromisoformat(fecha_inicio_str) if fecha_inicio_str else timezone.now().replace(day=1)
#             fecha_fin = datetime.fromisoformat(fecha_fin_str) if fecha_fin_str else timezone.now()
#         except ValueError:
#             return Response({"error": "Formato de fecha inválido. Use YYYY-MM-DD."}, status=400)

#         ventas_qs = Venta.objects.filter(fecha__range=(fecha_inicio, fecha_fin))
#         compras_qs = Compra.objects.filter(fecha__range=(fecha_inicio, fecha_fin))

#         total_ventas = ventas_qs.aggregate(total=Sum("total"))["total"] or 0
#         total_compras = compras_qs.aggregate(total=Sum("total"))["total"] or 0

#         utilidad_bruta = total_ventas - total_compras

#         return Response({
#             "ingresos": float(total_ventas),
#             "egresos": float(total_compras),
#             "utilidad_bruta": float(utilidad_bruta),
#             "moneda": "MXN",
#             "filtros": {
#                 "fecha_inicio": fecha_inicio.date().isoformat(),
#                 "fecha_fin": fecha_fin.date().isoformat()
#             }
#         })
