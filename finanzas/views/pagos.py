from finanzas.models import Pago
from finanzas.serializers import PagoSerializer
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class PagoViewSet(viewsets.ModelViewSet):
    """
    Listar todos los pagos y crear pagos nuevos.
    """
    queryset = Pago.objects.select_related('cuenta_cobrar', 'cuenta_pagar').all()
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pago = serializer.save()

        # La lógica para actualizar el estado se encuentra dentro del método save() del serializer

        return Response(serializer.data, status=status.HTTP_201_CREATED)