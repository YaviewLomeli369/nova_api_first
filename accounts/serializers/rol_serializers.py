from rest_framework import serializers
from accounts.models import Rol  # Importa el modelo correctamente

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'
