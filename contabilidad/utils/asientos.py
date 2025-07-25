from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable

def registrar_asiento_pago(pago, usuario):
    """
    Crea un asiento contable al registrar un pago a proveedor o cliente.
    """
    empresa = pago.empresa
    monto = pago.monto
    cuenta_banco = CuentaContable.objects.get(codigo='1020', empresa=empresa)

    if pago.cuenta_pagar:
        proveedor = pago.cuenta_pagar.proveedor
        cuenta_proveedor = CuentaContable.objects.get(codigo='2010', empresa=empresa)

        concepto = f"Pago a proveedor {proveedor.nombre}"
        descripcion = f"Disminución de cuenta por pagar a {proveedor.nombre}"

        asiento = AsientoContable.objects.create(
            empresa=empresa,
            fecha=pago.fecha,
            concepto=concepto,
            usuario=usuario,
            referencia_id=pago.id,
            referencia_tipo='Pago',
            es_automatico=True,
        )

        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_proveedor,
            debe=monto,
            descripcion=descripcion
        )
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_banco,
            haber=monto,
            descripcion="Pago realizado desde banco"
        )

    elif pago.cuenta_cobrar:
        cliente = pago.cuenta_cobrar.cliente
        cuenta_cliente = CuentaContable.objects.get(codigo='1050', empresa=empresa)

        concepto = f"Pago recibido de cliente {cliente.nombre}"
        descripcion = f"Disminución de cuenta por cobrar de {cliente.nombre}"

        asiento = AsientoContable.objects.create(
            empresa=empresa,
            fecha=pago.fecha,
            concepto=concepto,
            usuario=usuario,
            referencia_id=pago.id,
            referencia_tipo='Pago',
            es_automatico=True,
        )

        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_banco,
            debe=monto,
            descripcion="Ingreso en banco"
        )
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_cliente,
            haber=monto,
            descripcion=descripcion
        )
    else:
        raise ValueError("El pago no está vinculado ni a una cuenta por pagar ni por cobrar.")

    asiento.actualizar_totales()
    return asiento