from rest_framework import serializers
from finanzas.models import CuentaPorPagar

class CuentaPorPagarSerializer(serializers.ModelSerializer):
    compra_id = serializers.IntegerField(source='compra.id', read_only=True)
    proveedor_nombre = serializers.CharField(source='compra.proveedor.nombre', read_only=True)

    class Meta:
        model = CuentaPorPagar
        fields = [
            'id',
            'compra',
            'compra_id',
            'proveedor_nombre',
            'monto',
            'fecha_vencimiento',
            'estado',
        ]
