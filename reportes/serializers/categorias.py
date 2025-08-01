from rest_framework import serializers

class CategoriaRentableSerializer(serializers.Serializer):
    producto__categoria__id = serializers.IntegerField()
    producto__categoria__nombre = serializers.CharField()
    total_ingresos = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_costos = serializers.DecimalField(max_digits=20, decimal_places=2)
    utilidad = serializers.DecimalField(max_digits=20, decimal_places=2)
