from finanzas.models import CuentaPorCobrar
from rest_framework import serializers

class CuentaPorCobrarSerializer(serializers.ModelSerializer):
    venta = serializers.PrimaryKeyRelatedField(read_only=True)
    monto_pagado = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    saldo = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = CuentaPorCobrar
        fields = [
            'id',
            'venta',
            'monto',
            'monto_pagado',
            'saldo',
            'fecha_vencimiento',
            'estado',
            'notas',
        ]
        read_only_fields = ['id', 'monto_pagado', 'saldo', 'estado']
