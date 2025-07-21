from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable

def registrar_asiento_pago(pago, usuario):
    """
    Crea un asiento contable al registrar un pago a proveedor.
    """
    empresa = pago.empresa
    monto = pago.monto
    proveedor = pago.proveedor

    # Cuentas necesarias
    cuenta_banco = CuentaContable.objects.get(codigo='1020', empresa=empresa)
    cuenta_proveedor = CuentaContable.objects.get(codigo='2010', empresa=empresa)

    # Crear asiento
    asiento = AsientoContable.objects.create(
        empresa=empresa,
        fecha=pago.fecha_pago,
        concepto=f"Pago a proveedor {proveedor.nombre}",
        usuario=usuario,
        referencia_id=pago.id,
        referencia_tipo='Pago',
        es_automatico=True,
    )

    # Crear detalles (doble partida)
    DetalleAsiento.objects.create(
        asiento=asiento,
        cuenta_contable=cuenta_proveedor,
        debe=monto,
        descripcion=f"Disminución de cuenta por pagar a {proveedor.nombre}"
    )
    DetalleAsiento.objects.create(
        asiento=asiento,
        cuenta_contable=cuenta_banco,
        haber=monto,
        descripcion=f"Pago realizado desde banco"
    )

    # Actualiza totales del asiento
    asiento.actualizar_totales()

    return asiento