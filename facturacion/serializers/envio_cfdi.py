from facturacion.models import EnvioCorreoCFDI
from rest_framework import serializers

# facturacion/serializers.py
class EnvioCorreoCFDISerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvioCorreoCFDI
        fields = '__all__'