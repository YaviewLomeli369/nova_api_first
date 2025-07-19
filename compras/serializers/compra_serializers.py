from rest_framework import serializers
from compras.models import Proveedor, Compra, DetalleCompra
from compras.serializers.detalle_compra_serializers import DetalleCompraSerializer
from inventario.models import Inventario, MovimientoInventario
from django.db import transaction

class CompraSerializer(serializers.ModelSerializer):
    detalles = DetalleCompraSerializer(many=True)
    # total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total = serializers.SerializerMethodField()  # <- Cambiado
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


    def validate(self, data):
      detalles = data.get('detalles', [])
      productos = {}
  
      for detalle in detalles:
          producto = detalle['producto']
          lote = detalle.get('lote', '')
          fecha_vencimiento = detalle.get('fecha_vencimiento', None)
  
          # Usa un identificador único por producto, lote y fecha_vencimiento
          clave_producto = (producto.id, lote, fecha_vencimiento)
  
          if clave_producto in productos:
              raise serializers.ValidationError(
                  f"Producto duplicado: '{producto.nombre}' ya está incluido en los detalles con el mismo lote y fecha de vencimiento."
              )
  
          productos[clave_producto] = detalle
  
      return data

    def calcular_total_detalles(self, detalles_data):
        return sum(
            detalle['cantidad'] * detalle['precio_unitario']
            for detalle in detalles_data
        )

    def create(self, validated_data):
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

        detalles_data = validated_data.pop('detalles')

        total = self.calcular_total_detalles(detalles_data)
        validated_data['empresa'] = empresa
        validated_data['usuario'] = usuario
        validated_data['total'] = total

        with transaction.atomic():
            compra = Compra.objects.create(**validated_data)

            for detalle_data in detalles_data:
                DetalleCompra.objects.create(compra=compra, **detalle_data)

        return compra


    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if detalles_data is not None:
            instance.detalles.all().delete()
            total = 0
            for detalle_data in detalles_data:
                DetalleCompra.objects.create(compra=instance, **detalle_data)
                total += detalle_data['cantidad'] * detalle_data['precio_unitario']
            instance.total = total

        instance.save()
        return instance
