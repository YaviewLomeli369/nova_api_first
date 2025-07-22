from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from contabilidad.models import AsientoContable
from contabilidad.serializers.asiento_contable import AsientoContableSerializer
from rest_framework.exceptions import ValidationError


class AsientoContableViewSet(viewsets.ModelViewSet):
    queryset = AsientoContable.objects.all()
    serializer_class = AsientoContableSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['fecha', 'usuario', 'conciliado']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        empresa = getattr(self.request.user, 'empresa_actual', None)
        if empresa:
            return AsientoContable.objects.filter(empresa=empresa)\
                .select_related('empresa')\
                .prefetch_related('detalles')
        return AsientoContable.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['empresa'] = getattr(self.request.user, 'empresa_actual', None)
        return context

    def perform_create(self, serializer):
        empresa = getattr(self.request.user, 'empresa_actual', None)
        if not empresa:
            raise ValidationError("No se ha definido la empresa actual del usuario.")
        serializer.save(empresa=empresa)

    def update(self, request, *args, **kwargs):
        asiento = self.get_object()
        if asiento.conciliado:
            return Response(
                {"detail": "No se puede modificar un asiento contable ya conciliado."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)


    @action(detail=True, methods=['patch'], url_path='conciliar')
    def conciliar(self, request, pk=None):
        asiento = self.get_object()
        if asiento.conciliado:
            return Response({"detail": "Este asiento ya está conciliado."}, status=status.HTTP_400_BAD_REQUEST)

        asiento.conciliado = True
        asiento.save(update_fields=['conciliado'])
        return Response({"detail": "Asiento conciliado correctamente."}, status=status.HTTP_200_OK)