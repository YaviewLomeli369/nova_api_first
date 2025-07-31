from rest_framework import serializers
from ventas.models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ['id', 'creado_en', 'actualizado_en']


