from rest_framework import serializers

class EficienciaComprasSerializer(serializers.Serializer):
    planificadas = serializers.IntegerField()
    no_planificadas = serializers.IntegerField()
    urgentes = serializers.IntegerField()
    total_compras = serializers.IntegerField()
    costo_real_total = serializers.FloatField()
    presupuesto_total = serializers.FloatField()
    eficiencia = serializers.FloatField()
    ahorro = serializers.FloatField()

# # serializers/eficiencia_compras.py
# from rest_framework import serializers

# class EficienciaComprasSerializer(serializers.Serializer):
#     planificadas = serializers.IntegerField()
#     urgentes = serializers.IntegerField()
#     eficiencia = serializers.FloatField()
#     ahorro = serializers.FloatField()