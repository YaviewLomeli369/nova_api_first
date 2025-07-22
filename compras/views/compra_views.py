from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from compras.models import Compra
from compras.serializers import CompraSerializer
from accounts.permissions import IsSuperAdminOrCompras
from rest_framework import serializers
from decimal import Decimal
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from compras.models import Compra, DetalleCompra
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from inventario.models import Inventario
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from inventario.models import Inventario, MovimientoInventario
from compras.models import Compra, DetalleCompra
from datetime import datetime
from compras.filters import CompraFilter  # Importa el filtro
from contabilidad.helpers.asientos import generar_asiento_para_compra
import django_filters  # Asegúrate de que esta línea esté presente





class CompraReceiveView(APIView):
    def patch(self, request, pk):
        compra = get_object_or_404(Compra, pk=pk)

        if compra.estado == 'recibida':
            return Response({"detail": "Esta compra ya fue recibida."}, status=status.HTTP_400_BAD_REQUEST)

        detalles = DetalleCompra.objects.filter(compra=compra).select_for_update()

        with transaction.atomic():
            for detalle in detalles:
                cantidad_pendiente = detalle.cantidad - detalle.cantidad_recibida
                if cantidad_pendiente <= 0:
                    continue  # Ya recibido, no sumar más

                inventario, _ = Inventario.objects.select_for_update().get_or_create(
                    producto=detalle.producto,
                    sucursal=compra.usuario.sucursal_actual,
                    lote=detalle.lote or None,
                    fecha_vencimiento=detalle.fecha_vencimiento or None,
                    defaults={"cantidad": 0}
                )
                inventario.cantidad += cantidad_pendiente
                inventario.save()

                MovimientoInventario.objects.create(
                    inventario=inventario,
                    tipo_movimiento='entrada',
                    cantidad=cantidad_pendiente,
                    fecha=datetime.now(),
                    usuario=compra.usuario
                )

                detalle.cantidad_recibida = detalle.cantidad
                detalle.save()

            # Actualiza estado
            if all(d.cantidad_recibida >= d.cantidad for d in compra.detalles.all()):
                compra.estado = 'recibida'
            elif any(d.cantidad_recibida > 0 for d in compra.detalles.all()):
                compra.estado = 'parcial'
            else:
                compra.estado = 'pendiente'
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


# class CompraFilter(django_filters.FilterSet):
#     fecha_compra = django_filters.DateFilter(field_name='fecha', lookup_expr='exact')
#     fecha_min = django_filters.DateFilter(field_name='fecha', lookup_expr='gte')
#     fecha_max = django_filters.DateFilter(field_name='fecha', lookup_expr='lte')
#     total_min = django_filters.NumberFilter(field_name='total', lookup_expr='gte')
#     total_max = django_filters.NumberFilter(field_name='total', lookup_expr='lte')
#     nombre_producto = django_filters.CharFilter(method='filter_nombre_producto')
#     producto_id = django_filters.NumberFilter(field_name='detalles__producto__id')
#     producto_id__in = django_filters.BaseInFilter(field_name='detalles__producto__id', lookup_expr='in')

#     class Meta:
#         model = Compra
#         fields = ['empresa', 'proveedor', 'estado', 'fecha_compra']

#     def filter_nombre_producto(self, queryset, name, value):
#         return queryset.filter(detalles__producto__nombre__icontains=value).distinct()

# class CompraFilter(django_filters.FilterSet):
#     fecha_compra = django_filters.DateFilter(field_name='fecha', lookup_expr='exact')
#     nombre_producto = django_filters.CharFilter(method='filter_nombre_producto')

#     class Meta:
#         model = Compra
#         fields = ['empresa', 'proveedor', 'fecha_compra']

#     def filter_nombre_producto(self, queryset, name, value):
#         # Aquí usamos Q para hacer una búsqueda en la relación detalles -> producto -> nombre
#         return queryset.filter(
#             Q(detalles__producto__nombre__icontains=value)
#         ).distinct()  # Evita duplicados de compras que contienen varios productos coincidentes


# from rest_framework import viewsets, filters
# from django_filters.rest_framework import DjangoFilterBackend
# from .models import Compra
# from .serializers import CompraSerializer
# from .filters import CompraFilter


# /api/purchases/purchases/?search=camiseta
# /api/purchases/purchases/?proveedor=3
# /api/purchases/purchases/?fecha_min=2025-07-01&fecha_max=2025-07-31
# /api/purchases/purchases/?total_min=100&total_max=1000
# /api/purchases/purchases/?producto_id=7
# /api/purchases/purchases/?producto_id__in=5,7,8
# /api/purchases/purchases/?ordering=total
# /api/purchases/purchases/?ordering=-fecha


class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer

    filter_backends = [
        DjangoFilterBackend,       # Para filtros personalizados
        filters.SearchFilter,      # Para búsqueda general
        filters.OrderingFilter     # Para ordenamiento
    ]

    filterset_class = CompraFilter

    # Búsqueda tipo Google
    search_fields = [
        'detalles__producto__nombre',
        'detalles__producto__codigo',
        'proveedor__nombre',
        'detalles__lote'
    ]

    # Campos que se pueden ordenar
    ordering_fields = ['fecha', 'total']
    ordering = ['-fecha']  # Por defecto, mostrar compras recientes primero

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

        try:
            with transaction.atomic():
                compra = serializer.save(empresa=empresa, usuario=usuario)
                # Generar asiento contable
                asiento = generar_asiento_para_compra(compra, usuario)
        except Exception as e:
            raise serializers.ValidationError(f"Error al generar asiento contable: {str(e)}")



class CompraRecepcionParcialAPIView(APIView):
    def patch(self, request, pk):
        try:
            compra = Compra.objects.select_for_update().get(pk=pk)
        except Compra.DoesNotExist:
            return Response({'detail': 'Compra no encontrada.'}, status=404)

        data = request.data.get("items", [])
        if not data:
            return Response({'detail': 'No se enviaron productos a recibir.'}, status=400)

        resultados = []
        cambios_realizados = False

        with transaction.atomic():
            for item in data:
                detalle_id = item.get('detalle_id')
                recibido = item.get('recibido')

                if not detalle_id or recibido is None:
                    resultados.append({
                        'detalle_id': detalle_id,
                        'status': 'error',
                        'message': 'Faltan datos de detalle o cantidad recibida.'
                    })
                    continue

                try:
                    recibido = Decimal(recibido)
                except:
                    resultados.append({
                        'detalle_id': detalle_id,
                        'status': 'error',
                        'message': 'Cantidad recibida inválida.'
                    })
                    continue

                if recibido <= 0:
                    resultados.append({
                        'detalle_id': detalle_id,
                        'status': 'error',
                        'message': 'Cantidad recibida debe ser mayor a cero.'
                    })
                    continue

                try:
                    detalle = DetalleCompra.objects.select_for_update().get(id=detalle_id, compra=compra)
                except DetalleCompra.DoesNotExist:
                    resultados.append({
                        'detalle_id': detalle_id,
                        'status': 'error',
                        'message': 'Detalle no encontrado.'
                    })
                    continue

                cantidad_pendiente = detalle.cantidad - detalle.cantidad_recibida

                if cantidad_pendiente <= 0:
                    resultados.append({
                        'detalle_id': detalle_id,
                        'status': 'sin_cambios',
                        'message': 'Ya se recibió la cantidad completa para este detalle.'
                    })
                    continue

                recibido_real = min(recibido, cantidad_pendiente)

                # Actualiza cantidad recibida solo con lo que falta
                detalle.cantidad_recibida += recibido_real
                detalle.save()

                lote = detalle.lote or None
                vencimiento = detalle.fecha_vencimiento or None

                inventario, _ = Inventario.objects.select_for_update().get_or_create(
                    producto=detalle.producto,
                    sucursal=compra.usuario.sucursal_actual,
                    lote=lote,
                    fecha_vencimiento=vencimiento,
                    defaults={'cantidad': 0}
                )
                inventario.cantidad += recibido_real
                inventario.save()

                MovimientoInventario.objects.create(
                    inventario=inventario,
                    tipo_movimiento='entrada',
                    cantidad=recibido_real,
                    fecha=timezone.now(),
                    usuario=request.user
                )

                cambios_realizados = True

                resultados.append({
                    'detalle_id': detalle_id,
                    'status': 'recibido',
                    'cantidad_recibida': str(recibido_real),
                    'message': 'Cantidad recibida y stock actualizado.'
                })

            # Luego actualiza estado según cantidades recibidas
            if all(d.cantidad_recibida >= d.cantidad for d in compra.detalles.all()):
                compra.estado = 'recibida'
            elif any(d.cantidad_recibida > 0 for d in compra.detalles.all()):
                compra.estado = 'parcial'
            else:
                compra.estado = 'pendiente'
            compra.save()

        if cambios_realizados:
            return Response({
                'detail': 'Recepción procesada correctamente.',
                'resultados': resultados
            })
        else:
            return Response({
                'detail': 'No se realizaron cambios. Posiblemente todo ya estaba recibido.',
                'resultados': resultados
            }, status=400)


class CompraCancelarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        compra = get_object_or_404(Compra, pk=pk)

        # Si la compra ya está cancelada, no se debe hacer nada
        if compra.estado == 'cancelada':
            return Response({"detail": "La compra ya está cancelada."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si la compra ya fue recibida (parcial o completa)
        if compra.estado == 'recibida' or compra.estado == 'parcial':
            with transaction.atomic():
                for detalle in compra.detalles.all():
                    if detalle.cantidad_recibida > 0:
                        # Ajustar inventario y registrar movimiento de salida (devolución)
                        inventario = Inventario.objects.filter(
                            producto=detalle.producto,
                            sucursal=compra.usuario.sucursal_actual,
                            lote=detalle.lote,
                            fecha_vencimiento=detalle.fecha_vencimiento
                        ).first()

                        if inventario:
                            # Restar del inventario lo recibido
                            inventario.cantidad -= detalle.cantidad_recibida
                            inventario.save()

                            # Registrar el movimiento como salida (devolución)
                            MovimientoInventario.objects.create(
                                inventario=inventario,
                                tipo_movimiento='salida',  # Salida porque es una devolución
                                cantidad=detalle.cantidad_recibida,
                                fecha=timezone.now(),
                                usuario=request.user
                            )

                        # Resetear cantidad recibida a 0
                        detalle.cantidad_recibida = 0
                        detalle.save()

            compra.estado = 'cancelada'
            compra.save()
            return Response({"detail": "Compra cancelada y stock ajustado correctamente."}, status=status.HTTP_200_OK)

        # Si la compra no ha sido recibida aún, solo se cambia el estado a 'cancelada'
        compra.estado = 'cancelada'
        compra.save()

        return Response({"detail": "Compra cancelada correctamente, no se ajustó el inventario."}, status=status.HTTP_200_OK)
            
