from rest_framework import serializers

class FlujoCajaInputSerializer(serializers.Serializer):
    fecha_inicio = serializers.DateField(required=False)
    fecha_fin = serializers.DateField(required=False)

class FlujoCajaOutputSerializer(serializers.Serializer):
    ingresos = serializers.FloatField()
    egresos = serializers.FloatField()
    utilidad_bruta = serializers.FloatField()
    moneda = serializers.CharField()
    filtros = serializers.DictField()
