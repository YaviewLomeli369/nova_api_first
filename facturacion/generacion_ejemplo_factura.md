def construir_cfdi_para_facturama(venta, empresa, sucursal, cliente, folio="100", serie="A"):
# Aquí asumes que `venta` y `cliente` son diccionarios que ya tienes del frontend o API interna.

# RFC de pruebas
emisor_rfc = "CACX7605101P8"
emisor_nombre = "XOCHILT CASAS CHAVEZ"
emisor_regimen = "605"  # Sueldos y Salarios e Ingresos Asimilados a Salarios
sucursal_cp = "36257"   # Verificado para RFC CACX7605101P8

# Receptor puede ser el mismo en sandbox, o puedes variar con otros RFCs de prueba
receptor_rfc = "EKU9003173C9"
receptor_nombre = "ESCUELA KEMPER URGATE"
receptor_regimen = "601"
receptor_cp = "42501"

items = []
for idx, d in enumerate(venta["detalles"], start=1):
    unit_price = float(d["precio_unitario"])
    quantity = float(d["cantidad"])
    subtotal = unit_price * quantity
    iva = subtotal * 0.16

    item = {
        "ProductCode": "01010101",  # Clave genérica para productos
        "IdentificationNumber": f"{idx:03}",
        "Description": d["producto_nombre"],
        "Unit": "Unidad",
        "UnitCode": "H87",  # Unidad genérica SAT
        "UnitPrice": unit_price,
        "Quantity": quantity,
        "Subtotal": subtotal,
        "Discount": 0.0,
        "Total": subtotal + iva,
        "TaxObject": "02",  # Sí objeto de impuesto
        "Taxes": [
            {
                "Total": iva,
                "Name": "IVA",
                "Base": subtotal,
                "Rate": 0.16,
                "Type": "Traslado",
                "IsRetention": False
            }
        ]
    }
    items.append(item)

cfdi_data = {
    "Serie": serie,
    "Folio": folio,
    "CfdiType": "I",  # Ingreso
    "ExpeditionPlace": sucursal_cp,
    "PaymentConditions": "Contado",
    "PaymentMethod": "PUE",  # Pago en una sola exhibición
    "PaymentForm": "01",     # Efectivo
    "Currency": "MXN",
    "Exportation": "01",
    "Issuer": {
        "FiscalRegime": emisor_regimen,
        "Rfc": emisor_rfc,
        "Name": emisor_nombre
    },
    "Receiver": {
        "Rfc": receptor_rfc,
        "Name": receptor_nombre,
        "CfdiUse": "G01",           # Adquisición de mercancías
        "TaxZipCode": receptor_cp,
        "FiscalRegime": receptor_regimen
    },
    "Items": items
}

return cfdi_data