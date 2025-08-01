from rest_framework import serializers
from compras.models import PagoCompra

class PagoCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoCompra
        fields = '__all__'
        read_only_fields = ['id', 'creado_en', 'registrado_por']
