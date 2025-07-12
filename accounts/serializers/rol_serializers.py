from rest_framework import serializers
from ..models import Rol

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'