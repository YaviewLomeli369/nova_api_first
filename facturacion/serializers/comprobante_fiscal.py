# serializers.py

from rest_framework import serializers
from facturacion.models import ComprobanteFiscal
from ventas.models import Venta
from accounts.models import Usuario
from core.models import Empresa


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['id', 'nombre', 'rfc']  # Personaliza los campos que quieres incluir

class VentaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)

    class Meta:
        model = Venta
        fields = ['id', 'cliente_nombre']  # Personaliza los campos que quieres incluir

class ComprobanteFiscalSerializer(serializers.ModelSerializer):
    empresa = EmpresaSerializer(read_only=True)  # Relación anidada
    venta = VentaSerializer(read_only=True)  # Relación anidada
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    forma_pago_display = serializers.CharField(source='get_forma_pago_display', read_only=True)

    class Meta:
        model = ComprobanteFiscal
        fields = '__all__'  # También incluye todos los campos del modelo
