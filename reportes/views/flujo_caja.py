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


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from rest_framework import status
from reportes.services.flujo_de_caja import flujo_caja_proyectado

class FlujoCajaProyectadoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa = getattr(request.user, 'empresa', None)
        if not empresa:
            return Response({'detail': 'Usuario sin empresa asignada.'}, status=status.HTTP_400_BAD_REQUEST)

        fecha_inicio = parse_date(request.query_params.get('fecha_inicio')) if request.query_params.get('fecha_inicio') else None
        fecha_fin = parse_date(request.query_params.get('fecha_fin')) if request.query_params.get('fecha_fin') else None
        sucursal_id = request.query_params.get('sucursal_id')
        agrupacion = request.query_params.get('agrupacion', 'diaria')

        data = flujo_caja_proyectado(
            empresa=empresa,
            sucursal_id=sucursal_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            agrupacion=agrupacion,
        )

        return Response({
            'empresa': empresa.nombre,
            'sucursal_id': sucursal_id,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'agrupacion': agrupacion,
            'flujo_caja': data,
        })
