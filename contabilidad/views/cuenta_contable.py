# contabilidad/views/cuenta_contable.py

from rest_framework import viewsets, permissions
from contabilidad.models import CuentaContable
from contabilidad.serializers.cuenta_contable import CuentaContableSerializer
from django_filters.rest_framework import DjangoFilterBackend

class CuentaContableViewSet(viewsets.ModelViewSet):
    queryset = CuentaContable.objects.all()
    serializer_class = CuentaContableSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['empresa', 'codigo', 'padre']
    serializer_class = CuentaContableSerializer
    permission_classes = [permissions.IsAuthenticated]  # Aquí puedes agregar permisos personalizados

    def get_queryset(self):
        empresa = getattr(self.request.user, 'empresa_actual', None)
        if empresa:
            return CuentaContable.objects.filter(empresa=empresa).order_by('codigo')
        return CuentaContable.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['empresa'] = getattr(self.request.user, 'empresa_actual', None)
        return context
