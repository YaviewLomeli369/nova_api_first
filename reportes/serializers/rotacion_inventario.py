# reportes/serializers/rotacion_inventario.py

from rest_framework import serializers

class RotacionInventarioFiltroSerializer(serializers.Serializer):
    empresa_id = serializers.IntegerField(required=True)
    sucursal_id = serializers.IntegerField(required=False, allow_null=True)
    fecha_inicio = serializers.DateField(required=False, allow_null=True)
    fecha_fin = serializers.DateField(required=False, allow_null=True)
    agrupacion = serializers.ChoiceField(choices=['mensual', 'diaria'], default='mensual')

class RotacionInventarioResultadoSerializer(serializers.Serializer):
    periodo = serializers.CharField()
    costo_ventas = serializers.FloatField()
    inventario_inicial = serializers.FloatField()
    inventario_final = serializers.FloatField()
    inventario_promedio = serializers.FloatField()
    rotacion = serializers.FloatField()
    dias_promedio_inventario = serializers.FloatField(allow_null=True)

class RotacionInventarioResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    results = RotacionInventarioResultadoSerializer(many=True)
    totales = serializers.DictField()
    agrupacion = serializers.CharField()
    fecha_inicio = serializers.DateField(allow_null=True)
    fecha_fin = serializers.DateField(allow_null=True)


class RotacionInventarioSerializer(serializers.Serializer):
    periodo = serializers.CharField(read_only=True)
    costo_ventas = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    stock_promedio = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    rotacion = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)