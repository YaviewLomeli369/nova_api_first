from rest_framework import generics, permissions, serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.db import transaction
from django.core.exceptions import ValidationError

from compras.models import PagoCompra
from compras.serializers.pago import PagoCompraSerializer


class PagoCompraCreateView(generics.CreateAPIView):
    serializer_class = PagoCompraSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        compra = serializer.validated_data['compra']
        monto = serializer.validated_data['monto']

        if monto <= 0:
            raise DRFValidationError({"monto": "El monto debe ser mayor a cero."})

        if monto > compra.saldo_por_pagar:
            raise DRFValidationError({
                "monto": f"El monto excede el saldo pendiente de la compra. Saldo pendiente: {compra.saldo_por_pagar}"
            })

        try:
            with transaction.atomic():
                pago = serializer.save(usuario=self.request.user)
                compra.actualizar_estado_pago()
        except ValidationError as e:
            raise DRFValidationError(e.message_dict)


class PagoCompraListView(generics.ListAPIView):
    serializer_class = PagoCompraSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        compra_id = self.request.query_params.get('compra_id')
        if compra_id:
            return PagoCompra.objects.filter(compra_id=compra_id)
        return PagoCompra.objects.all()


class PagoCompraDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PagoCompra.objects.all()
    serializer_class = PagoCompraSerializer
    permission_classes = [permissions.IsAuthenticated]
