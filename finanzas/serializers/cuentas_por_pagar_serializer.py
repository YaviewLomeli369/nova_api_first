from rest_framework import serializers
from finanzas.models import CuentaPorPagar, Pago

class CuentaPorPagarSerializer(serializers.ModelSerializer):
    compra = serializers.PrimaryKeyRelatedField(read_only=True)
    monto_pagado = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    saldo = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = CuentaPorPagar
        fields = [
            'id',
            'compra',
            'monto',
            'monto_pagado',
            'saldo',
            'fecha_vencimiento',
            'estado',
        ]
        read_only_fields = ['id', 'monto_pagado', 'saldo', 'estado']
