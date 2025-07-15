from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from inventario.models import MovimientoInventario, Inventario
from inventario.serializers import MovimientoInventarioSerializer

from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions
from accounts.models import Auditoria  # 👈 Auditoría personalizada


class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

    def get_queryset(self):
        user = self.request.user
        return MovimientoInventario.objects.filter(inventario__producto__empresa=user.empresa).order_by('-fecha')

    def perform_create(self, serializer):
        movimiento = serializer.save(usuario=self.request.user)
        inventario = movimiento.inventario
        cantidad = movimiento.cantidad

        if movimiento.tipo_movimiento == 'salida':
            if cantidad > inventario.cantidad:
                raise serializers.ValidationError("No hay suficiente inventario para esta salida.")
            inventario.cantidad -= cantidad

        elif movimiento.tipo_movimiento == 'entrada':
            inventario.cantidad += cantidad

        elif movimiento.tipo_movimiento == 'ajuste':
            # Lógica personalizada según sea necesario
            pass

        inventario.full_clean()
        inventario.save()

        # 📝 Auditoría
        Auditoria.objects.create(
            usuario=self.request.user,
            accion='crear',
            tabla_afectada='MovimientoInventario',
            registro_afectado=f"ID: {movimiento.id}, Tipo: {movimiento.tipo_movimiento}, Cantidad: {movimiento.cantidad}"
        )

    def perform_update(self, serializer):
        movimiento = serializer.save()

        # No se actualiza inventario directamente desde aquí (recomendado)
        # Pero puedes auditar igual:
        Auditoria.objects.create(
            usuario=self.request.user,
            accion='actualizar',
            tabla_afectada='MovimientoInventario',
            registro_afectado=f"ID: {movimiento.id}, Tipo: {movimiento.tipo_movimiento}, Cantidad: {movimiento.cantidad}"
        )

    def perform_destroy(self, instance):
        # Guarda info antes de borrar
        info = f"ID: {instance.id}, Tipo: {instance.tipo_movimiento}, Cantidad: {instance.cantidad}"
        instance.delete()

        Auditoria.objects.create(
            usuario=self.request.user,
            accion='eliminar',
            tabla_afectada='MovimientoInventario',
            registro_afectado=info
        )






# from rest_framework import viewsets, serializers
# from rest_framework.permissions import IsAuthenticated
# from inventario.models import MovimientoInventario, Inventario
# from inventario.serializers import MovimientoInventarioSerializer

# from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions

# class MovimientoInventarioViewSet(viewsets.ModelViewSet):
#     serializer_class = MovimientoInventarioSerializer
#     permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

#     def get_queryset(self):
#         user = self.request.user
#         return MovimientoInventario.objects.filter(inventario__producto__empresa=user.empresa).order_by('-fecha')

#     def perform_create(self, serializer):
#         movimiento = serializer.save(usuario=self.request.user)
#         inventario = movimiento.inventario
#         cantidad = movimiento.cantidad

#         if movimiento.tipo_movimiento == 'salida':
#             if cantidad > inventario.cantidad:
#                 raise serializers.ValidationError("No hay suficiente inventario para esta salida.")
#             inventario.cantidad -= cantidad

#         elif movimiento.tipo_movimiento == 'entrada':
#             inventario.cantidad += cantidad

#         elif movimiento.tipo_movimiento == 'ajuste':
#             # Puedes definir reglas personalizadas si se desea
#             pass

#         # Validación final y guardado
#         inventario.full_clean()
#         inventario.save()



# # from rest_framework import viewsets
# # from rest_framework.permissions import IsAuthenticated
# # from inventario.models import MovimientoInventario
# # from inventario.serializers import MovimientoInventarioSerializer

# # from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsInventario, OrPermissions

# # class MovimientoInventarioViewSet(viewsets.ModelViewSet):
# #     serializer_class = MovimientoInventarioSerializer
# #     permission_classes = [IsAuthenticated, OrPermissions(IsSuperAdmin, IsEmpresaAdmin, IsInventario)]

# #     def get_queryset(self):
# #         user = self.request.user
# #         return MovimientoInventario.objects.filter(producto__empresa=user.empresa).order_by('-fecha')

# # # inventario/views/movimiento.py

# # from rest_framework import viewsets
# # from inventario.models import MovimientoInventario
# # from inventario.serializers import MovimientoInventarioSerializer

# # class MovimientoInventarioViewSet(viewsets.ModelViewSet):  # ✅ debe ser ModelViewSet
# #     queryset = MovimientoInventario.objects.all()
# #     serializer_class = MovimientoInventarioSerializer
