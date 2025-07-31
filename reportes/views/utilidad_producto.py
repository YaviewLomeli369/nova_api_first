# reportes/views/utilidad_producto.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from core.models import Sucursal

from reportes.services.utilidad_producto_service import reporte_utilidad_por_producto
from reportes.serializers.utilidad_producto_serializer import UtilidadProductoOutputSerializer
from reportes.models import ReporteGenerado

class ReporteUtilidadPorProductoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fecha_inicio = request.query_params.get("fecha_inicio")
        fecha_fin = request.query_params.get("fecha_fin")

        hoy = timezone.now().date()
        if not fecha_inicio:
            fecha_inicio = hoy.replace(day=1)
        if not fecha_fin:
            fecha_fin = hoy

        empresa = request.user.empresa_actual or request.user.empresa_set.first()
        sucursal = None
        sucursal_str = getattr(request.user, "sucursal_actual", None)

        if sucursal_str:
            try:
                # Intenta recuperar la sucursal por nombre
                sucursal = Sucursal.objects.get(nombre=sucursal_str, empresa=empresa)
            except Sucursal.DoesNotExist:
                # Manejar sucursal no encontrada, puedes dejarla en None
                pass

        data = reporte_utilidad_por_producto(fecha_inicio, fecha_fin, empresa, sucursal)

        filtros = {
            "fecha_inicio": fecha_inicio.isoformat() if hasattr(fecha_inicio, 'isoformat') else str(fecha_inicio),
            "fecha_fin": fecha_fin.isoformat() if hasattr(fecha_fin, 'isoformat') else str(fecha_fin),
            "sucursal": getattr(sucursal, "id", None),
        }

        ReporteGenerado.objects.create(
            nombre="Utilidad por producto",
            tipo="VENTAS",
            estado="COMPLETO",
            filtros_usados=filtros,
            generado_por=request.user,
            empresa=empresa,
        )

        serializer = UtilidadProductoOutputSerializer(data, many=True)
        return Response(serializer.data)
