from rest_framework import serializers
from reportes.filters.reporte_filter import ReporteVentasFilter
from reportes.models import ReporteGenerado
from reportes.utils.filtros import serializar_filtros
from reportes.services.calculos_kpis import ventas_agrupadas_por_fecha
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class FechaAgrupacionField(serializers.Field):
    def __init__(self, agrupacion, **kwargs):
        self.agrupacion = agrupacion
        super().__init__(**kwargs)

    def to_representation(self, value):
        if value is None:
            return None
        if self.agrupacion == 'dia':
            return value.strftime("%Y-%m-%d")
        elif self.agrupacion == 'mes':
            return value.strftime("%Y-%m")
        elif self.agrupacion == 'anio':
            return value.strftime("%Y")
        else:
            return str(value)  # fallback


class VentaAgrupadaSerializer(serializers.Serializer):
    fecha = FechaAgrupacionField(agrupacion=None, source='fecha_truncada')
    total_ventas = serializers.DecimalField(max_digits=10, decimal_places=2)

    def __init__(self, *args, **kwargs):
        agrupacion = kwargs.pop('agrupacion', None)
        super().__init__(*args, **kwargs)
        # Actualizar la agrupacion para el campo fecha
        self.fields['fecha'].agrupacion = agrupacion


class ReporteVentasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filtro = ReporteVentasFilter(data=request.query_params)
        filtro.is_valid(raise_exception=True)
        empresa = request.user.empresa_actual  # Ajusta según tu modelo de usuario

        datos_ventas = ventas_agrupadas_por_fecha(
            empresa=empresa,
            fecha_inicio=filtro.validated_data['fecha_inicio'],
            fecha_fin=filtro.validated_data['fecha_fin'],
            agrupacion=filtro.validated_data['agrupacion']
        )

        serializer = VentaAgrupadaSerializer(datos_ventas, many=True, agrupacion=filtro.validated_data['agrupacion'])

        # Para depurar:
        print(f"Datos ventas: {list(datos_ventas)}")
        print(f"Serializador: {serializer.data}")

        filtros_serializables = serializar_filtros(filtro.validated_data)

        ReporteGenerado.objects.create(
            nombre=f"Reporte de ventas agrupado por {filtro.validated_data['agrupacion']}",
            tipo="VENTAS",
            estado="COMPLETO",
            filtros_usados=filtros_serializables,
            generado_por=request.user,
            empresa=empresa
        )

        return Response(serializer.data)