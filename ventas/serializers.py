from rest_framework import serializers
from .models import Cliente, Venta, DetalleVenta
from inventario.models import Producto


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            'id',
            'empresa',
            'nombre',
            'rfc',
            'correo',
            'telefono',
            'direccion',
            'creado_en',
            'actualizado_en',
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']


from rest_framework import serializers
from django.db import transaction
from .models import Cliente, Venta, DetalleVenta
from inventario.models import Producto


class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = DetalleVenta
        fields = [
            'id',
            'producto',
            'producto_nombre',
            'cantidad',
            'precio_unitario',
            'subtotal',
        ]

    def get_subtotal(self, obj):
        return obj.cantidad * obj.precio_unitario


class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Venta
        fields = [
            'id',
            'empresa',
            'cliente',
            'cliente_nombre',
            'usuario',
            'usuario_username',
            'fecha',
            'total',
            'estado',
            'detalles',
        ]
        read_only_fields = ['id', 'fecha', 'total']

    @transaction.atomic
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        venta = Venta.objects.create(**validated_data)

        for detalle_data in detalles_data:
            producto_id = detalle_data['producto'].id

            # 🔒 Bloquear fila del producto
            producto = Producto.objects.select_for_update().get(id=producto_id)

            cantidad = detalle_data['cantidad']

            if producto.stock < cantidad:
                raise serializers.ValidationError(
                    f"No hay suficiente stock para el producto '{producto.nombre}'. Disponible: {producto.stock}"
                )

            producto.stock -= cantidad
            producto.save()

            DetalleVenta.objects.create(venta=venta, **detalle_data)

        return venta

    @transaction.atomic
    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if detalles_data is not None:
            # 🔁 Reponer stock de los detalles existentes
            for detalle in instance.detalles.all():
                producto = Producto.objects.select_for_update().get(id=detalle.producto.id)
                producto.stock += detalle.cantidad
                producto.save()

            # 🧹 Eliminar detalles antiguos
            instance.detalles.all().delete()

            # ➕ Crear nuevos detalles y descontar stock
            for detalle_data in detalles_data:
                producto = Producto.objects.select_for_update().get(id=detalle_data['producto'].id)
                cantidad = detalle_data['cantidad']

                if producto.stock < cantidad:
                    raise serializers.ValidationError(
                        f"No hay suficiente stock para el producto '{producto.nombre}'. Disponible: {producto.stock}"
                    )

                producto.stock -= cantidad
                producto.save()

                DetalleVenta.objects.create(venta=instance, **detalle_data)

        return instance


# class DetalleVentaSerializer(serializers.ModelSerializer):
#     producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
#     subtotal = serializers.SerializerMethodField()

#     class Meta:
#         model = DetalleVenta
#         fields = [
#             'id',
#             'producto',
#             'producto_nombre',
#             'cantidad',
#             'precio_unitario',
#             'subtotal',
#         ]

#     def get_subtotal(self, obj):
#         return obj.cantidad * obj.precio_unitario

#     def validate(self, data):
#         cantidad = data.get('cantidad')
#         precio_unitario = data.get('precio_unitario')
#         producto = data.get('producto')

#         if cantidad is None or cantidad <= 0:
#             raise serializers.ValidationError("La cantidad debe ser mayor a cero.")
#         if precio_unitario is None or precio_unitario <= 0:
#             raise serializers.ValidationError("El precio unitario debe ser mayor a cero.")
#         if producto is None:
#             raise serializers.ValidationError("El producto es obligatorio.")

#         if producto.stock < cantidad:
#             raise serializers.ValidationError(
#                 f"No hay suficiente stock para el producto '{producto.nombre}'. Stock disponible: {producto.stock}"
#             )

#         return data


# class VentaSerializer(serializers.ModelSerializer):
#     detalles = DetalleVentaSerializer(many=True)
#     cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
#     usuario_username = serializers.CharField(source='usuario.username', read_only=True)

#     class Meta:
#         model = Venta
#         fields = [
#             'id',
#             'empresa',
#             'cliente',
#             'cliente_nombre',
#             'usuario',
#             'usuario_username',
#             'fecha',
#             'total',  # calculado automáticamente por señal
#             'estado',
#             'detalles',
#         ]
#         read_only_fields = ['id', 'fecha', 'total']

#     def create(self, validated_data):
#         detalles_data = validated_data.pop('detalles')
#         venta = Venta.objects.create(**validated_data)

#         for detalle_data in detalles_data:
#             producto = detalle_data['producto']
#             cantidad = detalle_data['cantidad']

#             # Descontar stock
#             producto.stock -= cantidad
#             producto.save()

#             DetalleVenta.objects.create(venta=venta, **detalle_data)

#         return venta

#     def update(self, instance, validated_data):
#         detalles_data = validated_data.pop('detalles', None)

#         # Actualizar campos venta
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()

#         if detalles_data is not None:
#             # Reponer stock de detalles antiguos antes de eliminar
#             for detalle in instance.detalles.all():
#                 producto = detalle.producto
#                 producto.stock += detalle.cantidad
#                 producto.save()

#             # Eliminar detalles antiguos
#             instance.detalles.all().delete()

#             # Crear nuevos detalles y descontar stock
#             for detalle_data in detalles_data:
#                 producto = detalle_data['producto']
#                 cantidad = detalle_data['cantidad']

#                 producto.stock -= cantidad
#                 producto.save()

#                 DetalleVenta.objects.create(venta=instance, **detalle_data)

#         return instance

# from rest_framework import serializers
# from .models import Cliente, Venta, DetalleVenta
# from inventario.models import Producto


# class ClienteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Cliente
#         fields = [
#             'id',
#             'empresa',
#             'nombre',
#             'rfc',
#             'correo',
#             'telefono',
#             'direccion',
#             'creado_en',
#             'actualizado_en',
#         ]
#         read_only_fields = ['id', 'creado_en', 'actualizado_en']


# # class DetalleVentaSerializer(serializers.ModelSerializer):
# #     producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

# #     class Meta:
# #         model = DetalleVenta
# #         fields = [
# #             'id',
# #             'producto',
# #             'producto_nombre',
# #             'cantidad',
# #             'precio_unitario',
# #         ]

# #     def validate(self, data):
# #         cantidad = data.get('cantidad')
# #         precio_unitario = data.get('precio_unitario')
# #         producto = data.get('producto')

# #         if cantidad is None or cantidad <= 0:
# #             raise serializers.ValidationError("La cantidad debe ser mayor a cero.")
# #         if precio_unitario is None or precio_unitario <= 0:
# #             raise serializers.ValidationError("El precio unitario debe ser mayor a cero.")
# #         if producto is None:
# #             raise serializers.ValidationError("El producto es obligatorio.")

# #         # Aquí validamos el stock
# #         # Suponiendo que producto.stock es el inventario actual
# #         if producto.stock < cantidad:
# #             raise serializers.ValidationError(
# #                 f"No hay suficiente stock para el producto '{producto.nombre}'. Stock disponible: {producto.stock}"
# #             )

# #         return data


# class DetalleVentaSerializer(serializers.ModelSerializer):
#     producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
#     subtotal = serializers.SerializerMethodField()

#     class Meta:
#         model = DetalleVenta
#         fields = [
#             'id',
#             'producto',
#             'producto_nombre',
#             'cantidad',
#             'precio_unitario',
#             'subtotal',
#         ]

#     def get_subtotal(self, obj):
#         return obj.cantidad * obj.precio_unitario

#     def validate(self, data):
#         cantidad = data.get('cantidad')
#         precio_unitario = data.get('precio_unitario')
#         producto = data.get('producto')

#         if cantidad is None or cantidad <= 0:
#             raise serializers.ValidationError("La cantidad debe ser mayor a cero.")
#         if precio_unitario is None or precio_unitario <= 0:
#             raise serializers.ValidationError("El precio unitario debe ser mayor a cero.")
#         if producto is None:
#             raise serializers.ValidationError("El producto es obligatorio.")

#         # Validación de stock disponible
#         if producto.stock < cantidad:
#             raise serializers.ValidationError(
#                 f"No hay suficiente stock para el producto '{producto.nombre}'. Stock disponible: {producto.stock}"
#             )

#         return data



# # class VentaSerializer(serializers.ModelSerializer):
# #     detalles = DetalleVentaSerializer(many=True)
# #     cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
# #     usuario_username = serializers.CharField(source='usuario.username', read_only=True)

# #     class Meta:
# #         model = Venta
# #         fields = [
# #             'id',
# #             'empresa',
# #             'cliente',
# #             'cliente_nombre',
# #             'usuario',
# #             'usuario_username',
# #             'fecha',
# #             'total',
# #             'estado',
# #             'detalles',
# #         ]
# #         read_only_fields = ['id', 'fecha', 'total']  # total es solo lectura

# #     def create(self, validated_data):
# #         detalles_data = validated_data.pop('detalles')
# #         venta = Venta.objects.create(**validated_data)
# #         for detalle_data in detalles_data:
# #             DetalleVenta.objects.create(venta=venta, **detalle_data)
# #         # No calculamos ni guardamos total, la señal lo hará automáticamente
# #         return venta

# #     def update(self, instance, validated_data):
# #         detalles_data = validated_data.pop('detalles', None)
# #         for attr, value in validated_data.items():
# #             setattr(instance, attr, value)
# #         instance.save()

# #         if detalles_data is not None:
# #             instance.detalles.all().delete()
# #             for detalle_data in detalles_data:
# #                 DetalleVenta.objects.create(venta=instance, **detalle_data)
# #         # Tampoco calculamos total aquí; la señal actualiza total automáticamente
# #         return instance

# class VentaSerializer(serializers.ModelSerializer):
#     detalles = DetalleVentaSerializer(many=True)
#     cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
#     usuario_username = serializers.CharField(source='usuario.username', read_only=True)

#     class Meta:
#         model = Venta
#         fields = [
#             'id',
#             'empresa',
#             'cliente',
#             'cliente_nombre',
#             'usuario',
#             'usuario_username',
#             'fecha',
#             'total',   # Se calcula automáticamente por señal
#             'estado',
#             'detalles',
#         ]
#         read_only_fields = ['id', 'fecha', 'total']

#     def create(self, validated_data):
#         detalles_data = validated_data.pop('detalles')
#         venta = Venta.objects.create(**validated_data)

#         for detalle_data in detalles_data:
#             DetalleVenta.objects.create(venta=venta, **detalle_data)

#         return venta  # El total lo actualiza una señal

#     def update(self, instance, validated_data):
#         detalles_data = validated_data.pop('detalles', None)

#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()

#         if detalles_data is not None:
#             instance.detalles.all().delete()
#             for detalle_data in detalles_data:
#                 DetalleVenta.objects.create(venta=instance, **detalle_data)

#         return instance  # El total se actualizará por señal