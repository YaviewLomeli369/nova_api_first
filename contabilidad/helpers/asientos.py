from decimal import Decimal
from django.db import transaction
from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError

def redondear_decimal(valor, decimales=2):
    if not isinstance(valor, Decimal):
        valor = Decimal(str(valor))
    return valor.quantize(Decimal('1.' + '0' * decimales), rounding=ROUND_HALF_UP)

def generar_asiento_para_venta(venta, usuario):
    empresa = venta.empresa
    try:
        cuenta_clientes = CuentaContable.objects.get(codigo='1050', empresa=empresa)
        cuenta_ingresos = CuentaContable.objects.get(codigo='4010', empresa=empresa)
        cuenta_iva = CuentaContable.objects.get(codigo='2080', empresa=empresa)
    except ObjectDoesNotExist as e:
        raise ValidationError(f"No existe la cuenta contable requerida: {str(e)}")

    # Cálculo del total e IVA
    total = redondear_decimal(venta.total)
    iva_tasa = Decimal("0.16")
    base = redondear_decimal(total / (1 + iva_tasa))
    iva = redondear_decimal(total - base)

    with transaction.atomic():
        asiento = AsientoContable.objects.create(
            empresa=empresa,
            fecha=venta.fecha,
            concepto=f"Venta #{venta.id} a {venta.cliente.nombre}",
            usuario=usuario,
            referencia_id=venta.id,
            referencia_tipo='Venta',
            es_automatico=True,
        )

        # DEBE: Cliente por cobrar (total completo)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_clientes,
            debe=total,
            haber=Decimal('0.00'),
            descripcion="Venta - Cliente por cobrar"
        )

        # HABER: Ingresos (base sin IVA)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_ingresos,
            debe=Decimal('0.00'),
            haber=base,
            descripcion="Venta - Ingresos"
        )

        # HABER: IVA por pagar
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_iva,
            debe=Decimal('0.00'),
            haber=iva,
            descripcion="Venta - IVA por pagar"
        )

        asiento.actualizar_totales()
        venta.asiento_contable = asiento
        venta.save()
        return asiento


from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction

def generar_asiento_para_compra(compra, usuario):
    empresa = compra.empresa
    try:
        cuenta_costo = CuentaContable.objects.get(codigo='5010', empresa=empresa)
        cuenta_iva_acreditar = CuentaContable.objects.get(codigo='1180', empresa=empresa)
        cuenta_proveedores = CuentaContable.objects.get(codigo='2010', empresa=empresa)
    except ObjectDoesNotExist as e:
        raise ValidationError(f"No existe la cuenta contable requerida: {str(e)}")

    # Cálculo del total e IVA
    total = redondear_decimal(compra.total)
    iva_tasa = Decimal("0.16")
    base = redondear_decimal(total / (1 + iva_tasa))
    iva = redondear_decimal(total - base)

    with transaction.atomic():
        asiento = AsientoContable.objects.create(
            empresa=empresa,
            fecha=compra.fecha,
            concepto=f"Compra #{compra.id} de {compra.proveedor.nombre}",
            usuario=usuario,
            referencia_id=compra.id,
            referencia_tipo='Compra',
            es_automatico=True,
        )

        # DEBE: Costo de ventas (base sin IVA)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_costo,
            debe=base,
            haber=Decimal('0.00'),
            descripcion="Compra - Costo de ventas"
        )

        # DEBE: IVA por acreditar
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_iva_acreditar,
            debe=iva,
            haber=Decimal('0.00'),
            descripcion="Compra - IVA por acreditar"
        )

        # HABER: Proveedores por pagar (total completo)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_proveedores,
            debe=Decimal('0.00'),
            haber=total,
            descripcion="Compra - Proveedores por pagar"
        )

        asiento.actualizar_totales()
        # Se elimina la asignación para evitar error
        # compra.asiento_contable = asiento
        # compra.save()

        return asiento

# def generar_asiento_para_compra(compra, usuario):
#     empresa = compra.empresa
#     try:
#         cuenta_costo = CuentaContable.objects.get(codigo='5010', empresa=empresa)
#         cuenta_iva_acreditar = CuentaContable.objects.get(codigo='1180', empresa=empresa)
#         cuenta_proveedores = CuentaContable.objects.get(codigo='2010', empresa=empresa)
#     except ObjectDoesNotExist as e:
#         raise ValidationError(f"No existe la cuenta contable requerida: {str(e)}")

#     # Cálculo del total e IVA
#     total = redondear_decimal(compra.total)
#     iva_tasa = Decimal("0.16")
#     base = redondear_decimal(total / (1 + iva_tasa))
#     iva = redondear_decimal(total - base)

#     with transaction.atomic():
#         asiento = AsientoContable.objects.create(
#             empresa=empresa,
#             fecha=compra.fecha,
#             concepto=f"Compra #{compra.id} de {compra.proveedor.nombre}",
#             usuario=usuario,
#             referencia_id=compra.id,
#             referencia_tipo='Compra',
#             es_automatico=True,
#         )

#         # DEBE: Costo de ventas (base sin IVA)
#         DetalleAsiento.objects.create(
#             asiento=asiento,
#             cuenta_contable=cuenta_costo,
#             debe=base,
#             haber=Decimal('0.00'),
#             descripcion="Compra - Costo de ventas"
#         )

#         # DEBE: IVA por acreditar
#         DetalleAsiento.objects.create(
#             asiento=asiento,
#             cuenta_contable=cuenta_iva_acreditar,
#             debe=iva,
#             haber=Decimal('0.00'),
#             descripcion="Compra - IVA por acreditar"
#         )

#         # HABER: Proveedores por pagar (total completo)
#         DetalleAsiento.objects.create(
#             asiento=asiento,
#             cuenta_contable=cuenta_proveedores,
#             debe=Decimal('0.00'),
#             haber=total,
#             descripcion="Compra - Proveedores por pagar"
#         )

#         asiento.actualizar_totales()
#         compra.asiento_contable = asiento
#         compra.save()
#         return asiento