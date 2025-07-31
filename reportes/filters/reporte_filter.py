# reportes/filters/reporte_filter.py

from rest_framework import serializers

class ReporteVentasFilter(serializers.Serializer):
    fecha_inicio = serializers.DateField(required=True)
    fecha_fin = serializers.DateField(required=True)
    agrupacion = serializers.ChoiceField(choices=['dia', 'mes', 'anio'], default='dia')
