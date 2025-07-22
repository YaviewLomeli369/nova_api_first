# finanzas/signals.py

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from finanzas.models import Pago
from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable
from django.core.exceptions import ObjectDoesNotExist

# -------------------------
# Eliminar Asiento al borrar un Pago
# -------------------------

@receiver(post_delete, sender=Pago)
def eliminar_asiento_al_eliminar_pago(sender, instance, **kwargs):
    try:
        AsientoContable.objects.filter(
            referencia_id=instance.id,
            referencia_tipo='Pago',
            empresa=instance.empresa
        ).delete()
    except Exception as e:
        print(f"❌ Error eliminando asiento contable al borrar pago: {e}")


# -------------------------
# Crear Asiento al crear un Pago
# -------------------------

@receiver(post_save, sender=Pago)
def crear_asiento_para_pago(sender, instance, created, **kwargs):
    if not created or instance.asiento_contable_creado:
        return  # Evita duplicados

    try:
        # Buscar cuentas contables relacionadas al pago
        banco_cuenta = CuentaContable.objects.get(codigo='1020', empresa=instance.empresa)
        gasto_cuenta = CuentaContable.objects.get(codigo='6000', empresa=instance.empresa)
    except ObjectDoesNotExist as e:
        print(f"❌ Error: cuenta contable no encontrada: {e}")
        return

    try:
        # Crear asiento contable
        asiento = AsientoContable.objects.create(
            empresa=instance.empresa,
            fecha=instance.fecha,
            concepto=f'Pago automático #{instance.id}',
            usuario=instance.usuario,
            conciliado=False,
            referencia_id=instance.id,
            referencia_tipo='Pago',
            total_debe=instance.monto,
            total_haber=instance.monto,
            es_automatico=True,
        )

        # Cargar detalle del asiento (Banco - Haber)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=banco_cuenta,
            debe=0,
            haber=instance.monto,
            descripcion='Salida de dinero (Pago)'
        )

        # Cargar detalle del asiento (Gasto - Debe)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=gasto_cuenta,
            debe=instance.monto,
            haber=0,
            descripcion='Gasto generado por el pago'
        )

        # Marcar pago como ya registrado contablemente
        instance.asiento_contable_creado = True
        instance.save(update_fields=["asiento_contable_creado"])

    except Exception as e:
        print(f"❌ Error creando asiento contable para el pago: {e}")




# # finanzas/signals.py
# from django.db.models.signals import post_delete
# from django.dispatch import receiver
# from finanzas.models import Pago
# from contabilidad.models import AsientoContable

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from finanzas.models import Pago
# from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable

# @receiver(post_delete, sender=Pago)
# def eliminar_asiento_al_eliminar_pago(sender, instance, **kwargs):
#     try:
#         AsientoContable.objects.filter(
#             referencia_id=instance.id,
#             referencia_tipo='Pago',
#             empresa=instance.empresa
#         ).delete()
#     except Exception as e:
#         print(f"Error eliminando asiento contable al borrar pago: {e}")



# @receiver(post_save, sender=Pago)
# def crear_asiento_para_pago(sender, instance, created, **kwargs):
#     if not created or instance.asiento_contable_creado:
#         return  # Evitar duplicados

#     banco_cuenta = CuentaContable.objects.get(codigo='1020')  # Ejemplo: Banco
#     gasto_cuenta = CuentaContable.objects.get(codigo='6000')  # Ejemplo: Gasto general

#     asiento = AsientoContable.objects.create(
#         empresa=instance.empresa,
#         fecha=instance.fecha,
#         concepto=f'Pago automático #{instance.id}',
#         usuario=instance.usuario,
#         conciliado=False,
#         referencia_id=instance.id,
#         referencia_tipo='Pago',
#         total_debe=instance.monto,
#         total_haber=instance.monto,
#         es_automatico=True,
#     )

#     DetalleAsiento.objects.create(
#         asiento=asiento,
#         cuenta_contable=banco_cuenta,
#         debe=0,
#         haber=instance.monto,
#         descripcion='Salida de dinero (Pago)'
#     )

#     DetalleAsiento.objects.create(
#         asiento=asiento,
#         cuenta_contable=gasto_cuenta,
#         debe=instance.monto,
#         haber=0,
#         descripcion='Gasto generado por el pago'
#     )

#     # Marcar que ya fue generado para evitar duplicados
#     instance.asiento_contable_creado = True
#     instance.save(update_fields=["asiento_contable_creado"])
