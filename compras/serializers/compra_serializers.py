from rest_framework import serializers
from compras.models import Proveedor, Compra, DetalleCompra
from compras.serializers.detalle_compra_serializers import DetalleCompraSerializer
from inventario.models import Inventario, MovimientoInventario
from django.db import transaction
from finanzas.models import CuentaPorPagar
from datetime import timedelta
from contabilidad.helpers.asientos import generar_asiento_para_compra

class CompraSerializer(serializers.ModelSerializer):
    detalles = DetalleCompraSerializer(many=True)
    total = serializers.SerializerMethodField()
    nombre_proveedor = serializers.CharField(source='proveedor.nombre', read_only=True)

    class Meta:
        model = Compra
        fields = [
            'id', 'empresa', 'proveedor', 'nombre_proveedor', 'fecha', 'estado',
            'usuario', 'total', 'detalles'
        ]
        read_only_fields = ['id', 'total', 'usuario', 'empresa']

    def get_total(self, obj):
        return sum(det.cantidad * det.precio_unitario for det in obj.detalles.all())

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')

        request = self.context.get('request')
        usuario = request.user if request else None
        sucursal = getattr(usuario, 'sucursal_actual', None)
        empresa = getattr(usuario, 'empresa', None)

        if not usuario or not usuario.is_authenticated:
            raise serializers.ValidationError("Usuario no autenticado.")
        if not sucursal:
            raise serializers.ValidationError("El usuario no tiene una sucursal asignada.")
        if not empresa:
            raise serializers.ValidationError("El usuario no tiene empresa asignada.")

        with transaction.atomic():
            # Crear compra con total temporal 0
            compra = Compra.objects.create(
                empresa=empresa,
                usuario=usuario,
                proveedor=validated_data['proveedor'],
                fecha=validated_data.get('fecha'),
                estado=validated_data.get('estado', 'PENDIENTE'),
                total=0  # Total temporal
            )

            # Crear los detalles
            for detalle_data in detalles_data:
                DetalleCompra.objects.create(compra=compra, **detalle_data)

            # Recalcular total después de guardar detalles
            compra.total = compra.calcular_total()
            compra.save(update_fields=['total'])

            # ✅ Crear CuentaPorPagar
            fecha_vencimiento = compra.fecha + timedelta(days=30)
            CuentaPorPagar.objects.create(
                empresa=empresa,
                compra=compra,
                monto=compra.total,
                fecha_vencimiento=fecha_vencimiento,
                estado='PENDIENTE'
            )

            # ✅ Generar asiento contable después de todo
            generar_asiento_para_compra(compra, usuario)

        return compra
