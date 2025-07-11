from rest_framework import serializers
from .models import CuentaPorCobrar, CuentaPorPagar, Pago
from ventas.models import Venta
from compras.models import Compra


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


class PagoSerializer(serializers.ModelSerializer):
    cuenta_cobrar_id = serializers.PrimaryKeyRelatedField(
        queryset=CuentaPorCobrar.objects.all(), required=False, allow_null=True
    )
    cuenta_pagar_id = serializers.PrimaryKeyRelatedField(
        queryset=CuentaPorPagar.objects.all(), required=False, allow_null=True
    )
    tipo = serializers.SerializerMethodField()

    class Meta:
        model = Pago
        fields = [
            'id',
            'cuenta_cobrar_id',
            'cuenta_pagar_id',
            'monto',
            'fecha',
            'metodo_pago',
            'tipo',
        ]

    def get_tipo(self, obj):
        if obj.cuenta_cobrar:
            return "CxC"
        elif obj.cuenta_pagar:
            return "CxP"
        return "N/A"

    def validate(self, data):
        if not data.get('cuenta_cobrar_id') and not data.get('cuenta_pagar_id'):
            raise serializers.ValidationError("Debe vincularse a una cuenta por cobrar o por pagar.")
        return data
