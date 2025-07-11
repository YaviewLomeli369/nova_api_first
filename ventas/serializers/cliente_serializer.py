from rest_framework import serializers
from ventas.models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            'id',
            'empresa',
            'nombre',
            'rfc',
            'correo',
            'telefono',
            'direccion',
            'creado_en',
            'actualizado_en',
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']
