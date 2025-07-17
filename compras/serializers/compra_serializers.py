from rest_framework import serializers
from compras.models import Proveedor, Compra, DetalleCompra
from compras.serializers.detalle_compra_serializers import DetalleCompraSerializer
from inventario.models import Inventario, MovimientoInventario
from django.db import transaction

class CompraSerializer(serializers.ModelSerializer):
    detalles = DetalleCompraSerializer(many=True)
    total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    nombre_proveedor = serializers.CharField(source='proveedor.nombre', read_only=True)

    class Meta:
        model = Compra
        fields = [
            'id', 'empresa', 'proveedor', 'nombre_proveedor', 'fecha', 'estado',
            'usuario', 'total', 'detalles'
        ]
        read_only_fields = ['id', 'total', 'usuario', 'empresa']

    def validate(self, data):
      # Validar estado
      if data.get('estado') not in dict(Compra.ESTADO_CHOICES):
          raise serializers.ValidationError("Estado inválido.")

      # Validar duplicados en producto
      detalles = data.get('detalles', [])
      productos = set()

      for detalle in detalles:
          producto = detalle['producto']
          if producto.id in productos:
              raise serializers.ValidationError(
                  f"Producto duplicado: '{producto.nombre}' ya está incluido en los detalles."
              )
          productos.add(producto.id)

      return data

    # def validate(self, data):
    #     estado = data.get('estado')
    #     if estado and estado not in dict(Compra.ESTADO_CHOICES):
    #         raise serializers.ValidationError("Estado inválido.")

    #     # Validar duplicados en detalles
    #     detalles = data.get('detalles', [])
    #     combinaciones = set()

    #     for detalle in detalles:
    #         producto = detalle['producto']
    #         lote = detalle.get('lote')
    #         fecha_vencimiento = detalle.get('fecha_vencimiento')
    #         key = (producto.id, lote, fecha_vencimiento)

    #         if key in combinaciones:
    #             raise serializers.ValidationError(
    #                 f"Producto duplicado: '{producto.nombre}', lote '{lote}', vencimiento '{fecha_vencimiento}'."
    #             )
    #         combinaciones.add(key)

    #     return data

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
        total = sum([d['cantidad'] * d['precio_unitario'] for d in detalles_data])

        validated_data['empresa'] = empresa
        validated_data['usuario'] = usuario
        validated_data['total'] = total

        with transaction.atomic():
            compra = Compra.objects.create(**validated_data)

            for detalle_data in detalles_data:
                producto = detalle_data['producto']
                cantidad = detalle_data['cantidad']
                precio_unitario = detalle_data['precio_unitario']
                lote = detalle_data.get('lote')
                fecha_vencimiento = detalle_data.get('fecha_vencimiento')

                DetalleCompra.objects.create(
                    compra=compra,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    lote=lote,
                    fecha_vencimiento=fecha_vencimiento
                )

                inventario, creado = Inventario.objects.get_or_create(
                    producto=producto,
                    sucursal=sucursal,
                    lote=lote,
                    fecha_vencimiento=fecha_vencimiento,
                    defaults={'cantidad': 0}
                )
                inventario.cantidad += cantidad
                inventario.save()

                MovimientoInventario.objects.create(
                    inventario=inventario,
                    tipo_movimiento='entrada',
                    cantidad=cantidad,
                    usuario=usuario
                )

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
