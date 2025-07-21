# contabilidad/serializers/cuenta_contable.py

from rest_framework import serializers
from contabilidad.models import CuentaContable

class CuentaContableSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentaContable
        fields = ['id', 'codigo', 'nombre', 'clasificacion', 'empresa', 'es_auxiliar', 'padre', 'creada_en']
        read_only_fields = ['creada_en', 'empresa']

    def validate_codigo(self, value):
        empresa = self.context.get('empresa')
        if CuentaContable.objects.filter(codigo=value, empresa=empresa).exists():
            raise serializers.ValidationError("Ya existe una cuenta con ese código para esta empresa.")
        return value

    def validate(self, data):
        if data.get('padre') and data['padre'].empresa != self.context.get('empresa'):
            raise serializers.ValidationError("La cuenta padre debe pertenecer a la misma empresa.")
        return data

    def create(self, validated_data):
        empresa = self.context.get('empresa')
        validated_data['empresa'] = empresa
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # No permitimos cambiar empresa en update para evitar inconsistencias
        validated_data.pop('empresa', None)
        return super().update(instance, validated_data)
