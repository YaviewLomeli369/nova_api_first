from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from contabilidad.models import AsientoContable
from contabilidad.serializers.asiento_contable import AsientoContableSerializer


class AsientoContableViewSet(viewsets.ModelViewSet):
    queryset = AsientoContable.objects.all()
    serializer_class = AsientoContableSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['empresa'] = getattr(self.request.user, 'empresa_actual', None)
        return context

    @action(detail=True, methods=['patch'], url_path='conciliar')
    def conciliar(self, request, pk=None):
        asiento = self.get_object()
        if asiento.conciliado:
            return Response({"detail": "Este asiento ya está conciliado."}, status=status.HTTP_400_BAD_REQUEST)

        asiento.conciliado = True
        asiento.save(update_fields=['conciliado'])
        return Response({"detail": "Asiento conciliado correctamente."}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        asiento = self.get_object()
        if asiento.conciliado:
            return Response(
                {"detail": "No se puede modificar un asiento contable ya conciliado o cerrado."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)


# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from contabilidad.serializers.asiento_contable import AsientoContableSerializer
# from contabilidad.models import AsientoContable

# class AsientoContableViewSet(viewsets.ModelViewSet):
#     queryset = AsientoContable.objects.all()
#     serializer_class = AsientoContableSerializer
#     permission_classes = [IsAuthenticated]

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         # Pasa la empresa del usuario actual o del request si quieres
#         context['empresa'] = getattr(self.request.user, 'empresa_actual', None)
#         return context

#     @action(detail=True, methods=['patch'], url_path='conciliar')
#     def conciliar(self, request, pk=None):
#         asiento = self.get_object()
#         if asiento.conciliado:
#             return Response({"detail": "Este asiento ya está conciliado."}, status=status.HTTP_400_BAD_REQUEST)

#         asiento.conciliado = True
#         asiento.save(update_fields=['conciliado'])
#         return Response({"detail": "Asiento conciliado correctamente."}, status=status.HTTP_200_OK)

#     def update(self, request, *args, **kwargs):
#         asiento = self.get_object()
#         if asiento.conciliado:
#             return Response(
#                 {"detail": "No se puede modificar un asiento contable ya conciliado o cerrado."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         return super().update(request, *args, **kwargs)
