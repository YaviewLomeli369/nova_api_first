# reportes/serializers/costo_promedio.py
from rest_framework import serializers

class CostoPromedioPonderadoSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    cppp = serializers.FloatField()
    total_compras = serializers.IntegerField()
    total_unidades = serializers.IntegerField()
