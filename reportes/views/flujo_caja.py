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

        # Validar parámetros de entrada
        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')
        sucursal_id = request.query_params.get('sucursal_id')
        agrupacion = request.query_params.get('agrupacion', 'diaria')

        # Validar agrupación
        if agrupacion not in ['diaria', 'mensual']:
            return Response({
                'detail': 'El parámetro agrupacion debe ser "diaria" o "mensual".'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Parsear fechas con manejo de errores
        fecha_inicio = None
        fecha_fin = None
        
        if fecha_inicio_str:
            fecha_inicio = parse_date(fecha_inicio_str)
            if not fecha_inicio:
                return Response({
                    'detail': 'fecha_inicio debe estar en formato YYYY-MM-DD.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if fecha_fin_str:
            fecha_fin = parse_date(fecha_fin_str)
            if not fecha_fin:
                return Response({
                    'detail': 'fecha_fin debe estar en formato YYYY-MM-DD.'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Validar sucursal si se proporciona
        if sucursal_id:
            try:
                sucursal_id = int(sucursal_id)
                from core.models import Sucursal
                if not Sucursal.objects.filter(id=sucursal_id, empresa=empresa).exists():
                    return Response({
                        'detail': 'La sucursal especificada no existe o no pertenece a su empresa.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, TypeError):
                return Response({
                    'detail': 'sucursal_id debe ser un número entero válido.'
                }, status=status.HTTP_400_BAD_REQUEST)

        try:
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
                'fecha_inicio': fecha_inicio.isoformat() if fecha_inicio else None,
                'fecha_fin': fecha_fin.isoformat() if fecha_fin else None,
                'agrupacion': agrupacion,
                'flujo_caja': data,
            })
        except Exception as e:
            return Response({
                'detail': f'Error al generar el reporte: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
