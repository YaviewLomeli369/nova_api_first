# compras/serializers.py
from rest_framework import serializers
from compras.models import Proveedor, Compra, DetalleCompra
# from compras.models import Proveedor, Compra, DetalleCompra

from inventario.models import Producto

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = [
            'id', 'empresa', 'nombre', 'rfc', 'correo', 'telefono', 'direccion',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']