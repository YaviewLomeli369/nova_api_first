from finanzas.models import Pago, CuentaPorPagar, CuentaPorCobrar
from rest_framework import serializers
from django.core.exceptions import ValidationError

class PagoSerializer(serializers.ModelSerializer):
    cuenta_pagar = serializers.PrimaryKeyRelatedField(
        queryset=CuentaPorPagar.objects.all(), allow_null=True, required=False
    )
    cuenta_cobrar = serializers.PrimaryKeyRelatedField(
        queryset=CuentaPorCobrar.objects.all(), allow_null=True, required=False
    )
    saldo_actual = serializers.SerializerMethodField(read_only=True)
    tipo_cuenta = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Pago
        fields = [
            'id',
            'cuenta_pagar',
            'cuenta_cobrar',
            'monto',
            'fecha',
            'metodo_pago',
            'saldo_actual',
            'tipo_cuenta',
            'observaciones',
        ]
        read_only_fields = ['id', 'saldo_actual', 'tipo_cuenta']

    def get_saldo_actual(self, obj):
        if obj.cuenta_pagar:
            return obj.cuenta_pagar.saldo_pendiente
        if obj.cuenta_cobrar:
            return obj.cuenta_cobrar.saldo_pendiente
        return None

    def get_tipo_cuenta(self, obj):
        if obj.cuenta_pagar:
            return 'CuentaPorPagar'
        if obj.cuenta_cobrar:
            return 'CuentaPorCobrar'
        return None

    def validate(self, data):
        cuenta_pagar = data.get('cuenta_pagar')
        cuenta_cobrar = data.get('cuenta_cobrar')
        monto = data.get('monto')

        if not cuenta_pagar and not cuenta_cobrar:
            raise serializers.ValidationError("El pago debe estar vinculado a una cuenta por pagar o por cobrar.")
        if cuenta_pagar and cuenta_cobrar:
            raise serializers.ValidationError("El pago no puede estar vinculado a ambas cuentas a la vez.")

        # Obtener saldo pendiente para validar monto
        saldo_pendiente = None
        if cuenta_pagar:
            saldo_pendiente = cuenta_pagar.saldo_pendiente
        elif cuenta_cobrar:
            saldo_pendiente = cuenta_cobrar.saldo_pendiente

        if monto is None or monto <= 0:
            raise serializers.ValidationError("El monto del pago debe ser mayor a cero.")
        if saldo_pendiente is not None and monto > saldo_pendiente:
            raise serializers.ValidationError(f"El monto del pago (${monto}) no puede exceder el saldo pendiente (${saldo_pendiente}).")

        return data
