from rest_framework import serializers
from finanzas.models import CuentaPorCobrar

class CuentaPorCobrarSerializer(serializers.ModelSerializer):
    venta_id = serializers.IntegerField(source='venta.id', read_only=True)
    cliente_nombre = serializers.CharField(source='venta.cliente.nombre', read_only=True)

    class Meta:
        model = CuentaPorCobrar
        fields = [
            'id',
            'venta',
            'venta_id',
            'cliente_nombre',
            'monto',
            'fecha_vencimiento',
            'estado',
        ]
