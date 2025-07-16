from rest_framework import serializers
from core.models import Empresa
import re

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'

    def validate_rfc(self, value):
        # Validación básica de formato RFC mexicano
        pattern = r'^([A-ZÑ&]{3,4}) ?-? ?(\d{2})(\d{2})(\d{2}) ?-? ?([A-Z\d]{3})$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("El RFC no tiene un formato válido")
        # Validar que el RFC sea único
        if Empresa.objects.filter(rfc=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Este RFC ya está registrado")
        return value

    def validate_razon_social(self, value):
        # Evitar duplicados de razón social
        if Empresa.objects.filter(razon_social__iexact=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Esta razón social ya está registrada")
        return value
