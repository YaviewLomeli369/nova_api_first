from rest_framework import serializers
from facturacion.models import TimbradoLog

class TimbradoLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimbradoLog
        fields = ['id', 'fecha_intento', 'exito', 'mensaje_error', 'uuid_obtenido', 'facturama_id']