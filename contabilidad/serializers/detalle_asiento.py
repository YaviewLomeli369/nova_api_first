from rest_framework import serializers
from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable
from accounts.models import Usuario
from django.db import transaction


class DetalleAsientoSerializer(serializers.ModelSerializer):
  cuenta_contable_codigo = serializers.ReadOnlyField(source='cuenta_contable.codigo')
  cuenta_contable_nombre = serializers.ReadOnlyField(source='cuenta_contable.nombre')

  class Meta:
      model = DetalleAsiento
      fields = ['id', 'cuenta_contable', 'cuenta_contable_codigo', 'cuenta_contable_nombre', 'debe', 'haber', 'descripcion']

  def validate(self, data):
      debe = data.get('debe', 0)
      haber = data.get('haber', 0)

      if debe < 0 or haber < 0:
          raise serializers.ValidationError("Debe y Haber no pueden ser negativos.")
      if debe == 0 and haber == 0:
          raise serializers.ValidationError("Debe o Haber deben tener un valor distinto de cero.")
      if debe > 0 and haber > 0:
          raise serializers.ValidationError("No puede tener valores en ambos campos a la vez.")

      return data