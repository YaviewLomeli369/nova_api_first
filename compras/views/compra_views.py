from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from compras.models import Compra
from compras.serializers import CompraSerializer
from accounts.permissions import IsSuperAdminOrCompras
from rest_framework import serializers

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from compras.models import Compra, DetalleCompra
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from inventario.models import Inventario

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from inventario.models import Inventario, MovimientoInventario
from compras.models import Compra, DetalleCompra
from datetime import datetime

class CompraReceiveView(APIView):
    def patch(self, request, pk):
        compra = get_object_or_404(Compra, pk=pk)

        if compra.estado == 'RECIBIDA':
            return Response({"detail": "Esta compra ya fue recibida."}, status=status.HTTP_400_BAD_REQUEST)

        detalles = DetalleCompra.objects.filter(compra=compra)

        with transaction.atomic():
            for detalle in detalles.select_related('producto'):
                try:
                    inventario, _ = Inventario.objects.select_for_update().get_or_create(
                        producto=detalle.producto,
                        sucursal=compra.usuario.sucursal_actual,
                        lote=detalle.lote or None,
                        fecha_vencimiento=detalle.fecha_vencimiento or None,
                        defaults={"cantidad": 0}
                    )
                    inventario.cantidad += detalle.cantidad
                    inventario.save()

                    MovimientoInventario.objects.create(
                        inventario=inventario,
                        tipo_movimiento='ENTRADA',
                        cantidad=detalle.cantidad,
                        fecha=datetime.now(),
                        usuario=compra.usuario  # o request.user si prefieres
                    )

                except Exception as e:
                    return Response(
                        {"detail": f"Error al procesar producto {detalle.producto.nombre}: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            compra.estado = 'RECIBIDA'
            compra.save()

        return Response({"detail": "Compra recibida correctamente."}, status=status.HTTP_200_OK)


class ReceivePurchase(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        # Buscar la compra por ID
        compra = get_object_or_404(Compra, id=id)

        # Validar si el estado es "pendiente" o "parcial", no debería estar ya "recibida"
        if compra.estado not in ['pendiente', 'parcial']:
            raise ValidationError("La compra ya ha sido recibida o está cancelada.")

        # Actualizar el estado a 'recibida' (si ya es parcial o pendiente)
        compra.estado = 'recibida'
        compra.save()

        # Verificar que el usuario tiene sucursal asignada
        sucursal = request.user.sucursal_actual
        if not sucursal:
            raise ValidationError("El usuario no tiene una sucursal asignada.")

        # Actualizar el stock de los productos en inventario
        for detalle in compra.detalles.all():
            producto = detalle.producto
            cantidad = detalle.cantidad

            # Obtener el inventario para esa sucursal, lote y producto
            inventario, creado = Inventario.objects.get_or_create(
                producto=producto,
                sucursal=sucursal,  # Sucursal obtenida del usuario
                lote=detalle.lote,
                fecha_vencimiento=detalle.fecha_vencimiento,
                defaults={'cantidad': 0}
            )

            # Incrementar la cantidad en el inventario
            inventario.cantidad += cantidad
            inventario.save()

        return Response({"message": "Compra recibida y stock actualizado."}, status=status.HTTP_200_OK)

# Personaliza la respuesta de los errores de validación
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # Personaliza el formato de la respuesta de error
        if isinstance(exc, ValidationError):
            response.data = {"detail": response.data[0]}  # Cambia el arreglo por un mensaje directo

    return response



class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer
    # permission_classes = [IsSuperAdminOrCompras] # 👈 Asegúrate de tener este permiso
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'proveedor']
    # search_fields = ['factura', 'comentarios']
    search_fields = ['detalles__producto__nombre']

    # ordering_fields = [ 'creado_en']
    # ordering = []
    ordering_fields = ['fecha', 'total']
    ordering = ['-fecha']  # Orden descendente por defecto

    def get_queryset(self):
        usuario = self.request.user
        empresa = getattr(usuario, 'empresa', None)
        if empresa:
            return Compra.objects.filter(empresa=empresa)
        return Compra.objects.none()

    def perform_create(self, serializer):
        usuario = self.request.user
        empresa = usuario.empresa
        if not getattr(usuario, 'sucursal_actual', None):
            raise serializers.ValidationError("El usuario no tiene una sucursal asignada.")
        serializer.save(empresa=empresa, usuario=usuario)
