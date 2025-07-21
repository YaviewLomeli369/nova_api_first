from rest_framework import serializers
from contabilidad.models import DetalleAsiento

class DetalleAsientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleAsiento
        fields = ['id', 'asiento', 'cuenta_contable', 'debe', 'haber', 'descripcion']
        read_only_fields = ['id']

    def validate(self, data):
        debe = data.get('debe', 0)
        haber = data.get('haber', 0)

        if debe < 0 or haber < 0:
            raise serializers.ValidationError("Debe y Haber no pueden ser negativos.")

        if debe == 0 and haber == 0:
            raise serializers.ValidationError("Debe o Haber deben tener un valor distinto de cero.")

        if debe > 0 and haber > 0:
            raise serializers.ValidationError("No puede tener valores en Debe y Haber al mismo tiempo.")

        return data
