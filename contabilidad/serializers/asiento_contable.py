from rest_framework import serializers
from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable
from accounts.models import Usuario
from django.db import transaction
from contabilidad.serializers.detalle_asiento import DetalleAsientoSerializer

class AsientoContableSerializer(serializers.ModelSerializer):
    detalles = DetalleAsientoSerializer(many=True)
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), required=False, allow_null=True)
    empresa = serializers.PrimaryKeyRelatedField(read_only=True)
    total_debe = serializers.DecimalField(read_only=True, max_digits=14, decimal_places=2)
    total_haber = serializers.DecimalField(read_only=True, max_digits=14, decimal_places=2)
    conciliado = serializers.BooleanField(read_only=True)
    es_automatico = serializers.BooleanField(read_only=True)

    class Meta:
        model = AsientoContable
        fields = [
            'id', 'empresa', 'fecha', 'concepto', 'usuario', 'creado_en', 'conciliado',
            'referencia_id', 'referencia_tipo', 'total_debe', 'total_haber', 'es_automatico',
            'detalles'
        ]
        read_only_fields = ['creado_en']

    def validate(self, data):
        # Bloquear modificación si está conciliado
        if self.instance and self.instance.conciliado:
            raise serializers.ValidationError("No se puede modificar un asiento contable ya conciliado.")

        detalles = data.get('detalles', None)

        # Validar detalles solo si vienen en la petición
        if detalles is not None:
            if len(detalles) < 2:
                raise serializers.ValidationError("Debe haber al menos dos detalles en el asiento para cumplir partida doble.")

            total_debe = sum(d.get('debe', 0) for d in detalles)
            total_haber = sum(d.get('haber', 0) for d in detalles)

            if total_debe != total_haber:
                raise serializers.ValidationError(
                    "El total del debe debe ser igual al total del haber (partida doble)."
                )

        return data

    @transaction.atomic
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        empresa = self.context.get('empresa')
        if empresa:
            validated_data['empresa'] = empresa

        asiento = AsientoContable.objects.create(**validated_data)

        total_debe = 0
        total_haber = 0
        for detalle_data in detalles_data:
            detalle = DetalleAsiento.objects.create(asiento=asiento, **detalle_data)
            total_debe += detalle.debe
            total_haber += detalle.haber

        asiento.total_debe = total_debe
        asiento.total_haber = total_haber
        asiento.save(update_fields=['total_debe', 'total_haber'])
        return asiento

    @transaction.atomic
    def update(self, instance, validated_data):
        # Bloquear actualización si está conciliado
        if instance.conciliado:
            raise serializers.ValidationError("No se puede modificar un asiento contable ya conciliado.")

        detalles_data = validated_data.pop('detalles', None)

        # Actualizar campos permitidos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if detalles_data is not None:
            instance.detalles.all().delete()
            total_debe = 0
            total_haber = 0
            for detalle_data in detalles_data:
                detalle = DetalleAsiento.objects.create(asiento=instance, **detalle_data)
                total_debe += detalle.debe
                total_haber += detalle.haber

            instance.total_debe = total_debe
            instance.total_haber = total_haber
            instance.save(update_fields=['total_debe', 'total_haber'])

        return instance


        
# from rest_framework import serializers
# from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable
# from accounts.models import Usuario
# from django.db import transaction
# from contabilidad.serializers.detalle_asiento import DetalleAsientoSerializer

# class AsientoContableSerializer(serializers.ModelSerializer):
#     detalles = DetalleAsientoSerializer(many=True)
#     usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), required=False, allow_null=True)
#     empresa = serializers.PrimaryKeyRelatedField(read_only=True)
#     total_debe = serializers.DecimalField(read_only=True, max_digits=14, decimal_places=2)
#     total_haber = serializers.DecimalField(read_only=True, max_digits=14, decimal_places=2)
#     conciliado = serializers.BooleanField(read_only=True)
#     es_automatico = serializers.BooleanField(read_only=True)
    
#     class Meta:
#       model = AsientoContable
#       fields = [
#           'id', 'empresa', 'fecha', 'concepto', 'usuario', 'creado_en', 'conciliado',
#           'referencia_id', 'referencia_tipo', 'total_debe', 'total_haber', 'es_automatico',
#           'detalles'
#       ]
#       read_only_fields = ['creado_en']

    

#     def validate(self, data):
#         # Si estamos actualizando un objeto ya conciliado, no permitir cambios
#         if self.instance and self.instance.conciliado:
#             raise serializers.ValidationError("No se puede modificar un asiento contable ya conciliado.")

#         detalles = data.get('detalles', None)

#         # Solo validamos los detalles si vienen en la petición (por ejemplo, en actualizaciones parciales)
#         if detalles is not None:
#             if not detalles:
#                 raise serializers.ValidationError("Debe haber al menos un detalle en el asiento.")

#             total_debe = sum(d.get('debe', 0) for d in detalles)
#             total_haber = sum(d.get('haber', 0) for d in detalles)

#             if total_debe != total_haber:
#                 raise serializers.ValidationError(
#                     "El total del debe debe ser igual al total del haber (partida doble)."
#                 )

#         return data



#     @transaction.atomic
#     def create(self, validated_data):
#       detalles_data = validated_data.pop('detalles')
#       # Empresa la tomamos del contexto o se pasa al crear
#       empresa = self.context.get('empresa')
#       if empresa:
#           validated_data['empresa'] = empresa
    
#       asiento = AsientoContable.objects.create(**validated_data)
    
#       total_debe = 0
#       total_haber = 0
#       for detalle_data in detalles_data:
#           detalle = DetalleAsiento.objects.create(asiento=asiento, **detalle_data)
#           total_debe += detalle.debe
#           total_haber += detalle.haber
    
#       asiento.total_debe = total_debe
#       asiento.total_haber = total_haber
#       asiento.save(update_fields=['total_debe', 'total_haber'])
#       return asiento
    
    
#     @transaction.atomic
#     def update(self, instance, validated_data):
#       detalles_data = validated_data.pop('detalles', None)
    
#       # Solo actualizar campos permitidos
#       for attr, value in validated_data.items():
#           setattr(instance, attr, value)
#       instance.save()
    
#       if detalles_data is not None:
#           # Eliminar detalles previos y crear nuevos (puedes cambiar esta lógica si quieres editar individualmente)
#           instance.detalles.all().delete()
#           total_debe = 0
#           total_haber = 0
#           for detalle_data in detalles_data:
#               detalle = DetalleAsiento.objects.create(asiento=instance, **detalle_data)
#               total_debe += detalle.debe
#               total_haber += detalle.haber
    
#           instance.total_debe = total_debe
#           instance.total_haber = total_haber
#           instance.save(update_fields=['total_debe', 'total_haber'])
    
#       return instance