# utils/build_facturama_payload.py

def build_facturama_payload(comprobante):
    venta = comprobante.venta
    cliente = venta.cliente
    empresa = comprobante.empresa

    items = []
    for detalle in venta.detalles.all():
        items.append({
            "ProductCode": detalle.producto.clave_sat,
            "IdentificationNumber": detalle.producto.codigo,
            "Description": detalle.producto.nombre,
            "Unit": detalle.producto.unidad_medida,
            "UnitCode": detalle.producto.unidad_medida,
            "UnitPrice": float(detalle.precio_unitario),
            "Quantity": float(detalle.cantidad),
            "Subtotal": float(detalle.importe),
            "Discount": 0.0,  # Si tienes descuento, ajusta aquí
            "Total": float(detalle.importe) * 1.16,  # Ejemplo IVA 16% incluido
            "TaxObject": "02",  # Asumiendo traslado
            "Taxes": [
                {
                    "Total": float(detalle.importe) * 0.16,
                    "Name": "IVA",
                    "Base": float(detalle.importe),
                    "Rate": 0.16,
                    "Type": "Traslado",
                    "IsRetention": False,
                }
            ],
        })

    payload = {
        "Serie": comprobante.serie or "A",
        "Folio": comprobante.folio or "100",
        "CfdiType": comprobante.tipo_comprobante or "I",
        "ExpeditionPlace": empresa.codigo_postal,
        "PaymentConditions": comprobante.condiciones_pago or "Contado",
        "PaymentMethod": comprobante.metodo_pago or "PUE",
        "PaymentForm": comprobante.forma_pago or "01",
        "Currency": comprobante.moneda or "MXN",
        "Exportation": "01",  # Valor fijo o configurable
        "Issuer": {
            "FiscalRegime": empresa.regimen_fiscal or "601",
            "Rfc": empresa.rfc,
            "Name": empresa.razon_social,
        },
        "Receiver": {
            "Rfc": cliente.rfc,
            "Name": cliente.nombre_completo,
            "CfdiUse": cliente.uso_cfdi or "S01",
            "TaxZipCode": cliente.codigo_postal or empresa.codigo_postal,
            "FiscalRegime": cliente.regimen_fiscal or "601",
        },
        "Items": items,
    }

    return payload