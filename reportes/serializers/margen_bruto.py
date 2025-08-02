# reportes/serializers.py

from rest_framework import serializers

class MargenBrutoFiltroSerializer(serializers.Serializer):
    empresa_id = serializers.IntegerField()
    sucursal_id = serializers.IntegerField(required=False, allow_null=True)
    fecha_inicio = serializers.DateField(required=False, allow_null=True)
    fecha_fin = serializers.DateField(required=False, allow_null=True)
    agrupacion = serializers.ChoiceField(choices=['diaria', 'mensual'], default='mensual')

class MargenBrutoDetalleSerializer(serializers.Serializer):
    periodo = serializers.CharField()
    ventas = serializers.FloatField()
    costo = serializers.FloatField()
    margen_bruto = serializers.FloatField()

class MargenBrutoResponseSerializer(serializers.Serializer):
    detalle = MargenBrutoDetalleSerializer(many=True)
    totales = serializers.DictField()
