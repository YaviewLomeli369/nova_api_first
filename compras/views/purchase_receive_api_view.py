# from django.db import transaction
# from django.db.models import Q

# class PurchaseReceiveAPIView(generics.UpdateAPIView):
#     queryset = Compra.objects.all()
#     serializer_class = CompraSerializer

#     def partial_update(self, request, *args, **kwargs):
#         compra = self.get_object()

#         if compra.estado != 'pendiente':
#             return Response({'error': 'La compra ya fue recibida o cancelada.'}, status=status.HTTP_400_BAD_REQUEST)

#         detalles = compra.detalles.all()

#         with transaction.atomic():
#             for detalle in detalles.select_related('producto'):
#                 try:
#                     producto = detalle.producto
#                     sucursal = request.user.sucursal_actual
#                     lote = detalle.lote or None
#                     fecha_venc = detalle.fecha_vencimiento or None

#                     # 🔐 Bloqueamos filas para evitar condiciones de carrera
#                     inventario, _ = Inventario.objects.select_for_update().get_or_create(
#                         producto=producto,
#                         sucursal=sucursal,
#                         lote=lote,
#                         fecha_vencimiento=fecha_venc,
#                         defaults={'cantidad': 0}
#                     )

#                     # 📥 Aumentamos la cantidad en stock
#                     inventario.cantidad += detalle.cantidad
#                     inventario.save()

#                     # 📋 Registramos el movimiento de entrada
#                     MovimientoInventario.objects.create(
#                         inventario=inventario,
#                         tipo_movimiento='entrada',
#                         cantidad=detalle.cantidad,
#                         fecha=timezone.now(),
#                         usuario=request.user  # ⚠️ Verifica que tu modelo tenga `usuario`
#                     )

#                 except Exception as e:
#                     return Response({
#                         'error': f'Error al procesar producto {producto.nombre}',
#                         'detalle': str(e)
#                     }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#             # ✅ Actualizamos estado de la compra
#             compra.estado = 'recibida'
#             compra.save()

#         return Response({'mensaje': 'Compra recibida correctamente.'})
