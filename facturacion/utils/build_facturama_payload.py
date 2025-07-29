# utils/build_facturama_payload.py

from decimal import Decimal
from facturacion.utils.facturama_helpers import tipo_cfdi_desde_tipo_comprobante
import json  # para impresión legible

def build_facturama_payload(comprobante):
    venta = comprobante.venta
    cliente = venta.cliente
    empresa = comprobante.empresa

    items = []
    for detalle in venta.detalles.all():
        producto = detalle.producto
        cantidad = Decimal(detalle.cantidad)
        precio_unitario = Decimal(detalle.precio_unitario)
        subtotal = cantidad * precio_unitario
        tasa_iva = Decimal("0.16")
        iva = subtotal * tasa_iva
        total = subtotal + iva

        items.append({
            "ProductCode": getattr(producto.clave_sat.clave, 'clave', "01010101"),
            "IdentificationNumber": producto.codigo or "",
            "Description": producto.nombre,
            "Unit": getattr(producto.unidad_medida, 'descripcion', "Unidad"),
            "UnitCode": getattr(producto.unidad_medida, 'clave', "H87"),
            "UnitPrice": float(precio_unitario),
            "Quantity": float(cantidad),
            "Subtotal": float(subtotal),
            "Discount": 0.0,  # Mejora: incluir detalle.descuento si aplica
            "Total": float(total),
            "TaxObject": "02",  # Gravado
            "Taxes": [
                {
                    "Total": float(iva),
                    "Name": "IVA",
                    "Base": float(subtotal),
                    "Rate": float(tasa_iva),
                    "Type": "Traslado",
                    "IsRetention": False,
                }
            ],
        })

    payload = {
        "Serie": comprobante.serie or "A",
        "Folio": comprobante.folio or "100",
        "CfdiType": tipo_cfdi_desde_tipo_comprobante(comprobante.tipo),
        "ExpeditionPlace": empresa.domicilio_codigo_postal or "00000",
        "PaymentConditions": venta.condiciones_pago or "Contado",
        "PaymentMethod": venta.metodo_pago or "PUE",  # Pago en una sola exhibición
        "PaymentForm": venta.forma_pago or "01",      # Efectivo
        "Currency": venta.moneda or "MXN",
        "Exportation": "01",  # No aplica exportación
        "Issuer": {
            "FiscalRegime": str(empresa.regimen_fiscal) if empresa.regimen_fiscal else "601",
            "Rfc": empresa.rfc,
            "Name": empresa.razon_social,
        },
        "Receiver": {
            "Rfc": cliente.rfc,
            "Name": cliente.nombre_completo,
            "CfdiUse": cliente.uso_cfdi or "S01",  # Por definir
            "TaxZipCode": cliente.direccion_codigo_postal or empresa.domicilio_codigo_postal,
            "FiscalRegime": int(cliente.regimen_fiscal) if cliente.regimen_fiscal else 601,
        },
        "Items": items,
    }
    print("Payload que se enviará a Facturama:")
    print(json.dumps(payload, indent=4, ensure_ascii=False))


    return payload
