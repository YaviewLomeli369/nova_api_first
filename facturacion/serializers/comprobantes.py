from rest_framework import serializers
from facturacion.models import ComprobanteFiscal

class ComprobanteFiscalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComprobanteFiscal
        fields = '__all__'
        read_only_fields = [
            'uuid', 'xml', 'pdf', 'fecha_timbrado',
            'estado', 'error_mensaje', 'created_at', 'updated_at'
        ]
