from rest_framework import serializers
from ..models import Auditoria

class AuditoriaSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()

    class Meta:
        model = Auditoria
        fields = [
            'id',
            'usuario',
            'accion',
            'tabla_afectada',
            'registro_afectado',
            'timestamp',
        ]
