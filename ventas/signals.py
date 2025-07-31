# ventas/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, F
from django.utils import timezone
from .models import DetalleVenta, Venta

def actualizar_total_venta(venta_id):
    try:
        venta = Venta.objects.get(id=venta_id)
    except Venta.DoesNotExist:
        return  # Si no existe, nada que hacer

    total = venta.detalles.aggregate(
        total=Sum(F('cantidad') * F('precio_unitario'))
    )['total'] or 0

    # Actualizar solo si cambió para evitar saves innecesarios
    if venta.total != total:
        venta.total = total
        venta.save(update_fields=['total'])

def procesar_movimiento_inventario_venta(detalle_venta, operacion='crear'):
    """
    Procesa el movimiento de inventario cuando se crea o elimina un detalle de venta
    """
    from inventario.models import Inventario, MovimientoInventario
    
    # Solo procesar si la venta está completada
    if detalle_venta.venta.estado != 'COMPLETADA':
        return
    
    try:
        # Buscar inventario del producto en la sucursal del usuario
        sucursal_usuario = detalle_venta.venta.usuario.sucursal_actual
        if not sucursal_usuario:
            print(f"Usuario {detalle_venta.venta.usuario.username} no tiene sucursal actual")
            return
            
        inventario = Inventario.objects.filter(
            producto=detalle_venta.producto,
            sucursal=sucursal_usuario
        ).first()
        
        if not inventario:
            print(f"No se encontró inventario para {detalle_venta.producto.nombre} en {sucursal_usuario.nombre}")
            return
            
        if operacion == 'crear':
            # Verificar que hay suficiente stock
            if inventario.cantidad < detalle_venta.cantidad:
                print(f"Stock insuficiente para {detalle_venta.producto.nombre}. Disponible: {inventario.cantidad}, Requerido: {detalle_venta.cantidad}")
                return
                
            # Decrementar stock
            inventario.cantidad -= detalle_venta.cantidad
            inventario.save()
            
            # Crear movimiento de salida
            MovimientoInventario.objects.create(
                inventario=inventario,
                tipo_movimiento='salida',
                cantidad=detalle_venta.cantidad,
                fecha=timezone.now(),
                usuario=detalle_venta.venta.usuario
            )
            
        elif operacion == 'eliminar':
            # Incrementar stock (devolución)
            inventario.cantidad += detalle_venta.cantidad
            inventario.save()
            
            # Crear movimiento de entrada (devolución)
            MovimientoInventario.objects.create(
                inventario=inventario,
                tipo_movimiento='entrada',
                cantidad=detalle_venta.cantidad,
                fecha=timezone.now(),
                usuario=detalle_venta.venta.usuario
            )
            
    except Exception as e:
        print(f"Error al procesar movimiento de inventario: {e}")

@receiver(post_save, sender=DetalleVenta)
def detalleventa_guardado(sender, instance, created, **kwargs):
    actualizar_total_venta(instance.venta_id)
    
    # Solo procesar movimientos de inventario para nuevos detalles
    if created:
        procesar_movimiento_inventario_venta(instance, 'crear')

@receiver(post_delete, sender=DetalleVenta)
def detalleventa_eliminado(sender, instance, **kwargs):
    actualizar_total_venta(instance.venta_id)
    procesar_movimiento_inventario_venta(instance, 'eliminar')

@receiver(post_save, sender=Venta)
def venta_guardada(sender, instance, created, **kwargs):
    """
    Procesa movimientos de inventario cuando cambia el estado de una venta
    """
    if not created and instance.estado == 'COMPLETADA':
        # Si la venta se marcó como completada, procesar todos sus detalles
        for detalle in instance.detalles.all():
            procesar_movimiento_inventario_venta(detalle, 'crear')
