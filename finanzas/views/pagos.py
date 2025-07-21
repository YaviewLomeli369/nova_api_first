from finanzas.models import Pago
from finanzas.serializers import PagoSerializer
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from contabilidad.utils.asientos import registrar_asiento_pago
from rest_framework.exceptions import ValidationError
from contabilidad.models import AsientoContable

class PagoViewSet(viewsets.ModelViewSet):
    # ...
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pago = serializer.save()

        # Crear asiento contable automático
        try:
            registrar_asiento_pago(pago, request.user)
        except Exception as e:
            # Loguear error en consola (puedes usar logging)
            print(f"Error al registrar asiento contable: {e}")
            # Retornar respuesta exitosa pero con advertencia
            return Response({
                "pago": PagoSerializer(pago).data,
                "advertencia": f"No se pudo registrar el asiento contable: {str(e)}"
            }, status=status.HTTP_201_CREATED)

        return Response(PagoSerializer(pago).data, status=status.HTTP_201_CREATED)


    def destroy(self, request, *args, **kwargs):
        pago = self.get_object()

        asiento = AsientoContable.objects.filter(
            referencia_id=pago.id,
            referencia_tipo='Pago',
            empresa=pago.empresa
        ).first()

        if asiento and asiento.conciliado:
            raise ValidationError("No se puede eliminar este pago porque su asiento contable ya está conciliado o cerrado.")

        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        pago = self.get_object()
        asiento = AsientoContable.objects.filter(
            referencia_id=pago.id,
            referencia_tipo='Pago',
            empresa=pago.empresa
        ).first()

        if asiento and asiento.conciliado:
            return Response(
                {"detail": "No se puede modificar este pago porque su asiento contable ya está conciliado o cerrado."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

