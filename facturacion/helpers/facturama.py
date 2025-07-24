import requests
import base64
from django.conf import settings

FACTURAMA_BASE_URL = "https://apisandbox.facturama.mx"

def timbrar_cfdi_venta(venta):
    """
    Envía la venta a Facturama para timbrar y devuelve la respuesta JSON.
    """
    # Autenticación básica
    user_pass = f"{settings.FACTURAMA_USER}:{settings.FACTURAMA_PASSWORD}"
    token = base64.b64encode(user_pass.encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

    # Construir JSON dinámico usando datos reales de la venta
    cfdi_data = {
        "Serie": "A",
        "Folio": str(venta.id),  # Puedes ajustar lógica de folio si quieres
        "CfdiType": "I",
        "ExpeditionPlace": venta.empresa.codigo_postal or "00000",
        "PaymentConditions": "Contado",
        "PaymentMethod": venta.metodo_pago or "PUE",
        "PaymentForm": venta.forma_pago or "01",
        "Currency": "MXN",
        "Exportation": "01",
        "Issuer": {
            "FiscalRegime": venta.empresa.regimen_fiscal_codigo,
            "Rfc": venta.empresa.rfc,
            "Name": venta.empresa.nombre
        },
        "Receiver": {
            "Rfc": venta.cliente.rfc,
            "Name": venta.cliente.nombre,
            "CfdiUse": venta.uso_cfdi,
            "TaxZipCode": getattr(venta.cliente, 'codigo_postal', "00000"),
            "FiscalRegime": getattr(venta.cliente, 'regimen_fiscal_codigo', "601")
        },
        "Items": []
    }

    for detalle in venta.detalleventa_set.all():
        item = {
            "ProductCode": detalle.producto.clave_producto or "01010101",
            "IdentificationNumber": detalle.lote or "001",
            "Description": detalle.producto.nombre,
            "Unit": detalle.producto.unidad or "ACT",
            "UnitCode": detalle.producto.clave_unidad or "ACT",
            "UnitPrice": float(detalle.precio_unitario),
            "Quantity": float(detalle.cantidad),
            "Subtotal": float(detalle.importe),
            "Discount": 0.0,
            "Total": round(detalle.importe * 1.16, 2),  # IVA 16%
            "TaxObject": "02",
            "Taxes": [
                {
                    "Total": round(detalle.importe * 0.16, 2),
                    "Name": "IVA",
                    "Base": float(detalle.importe),
                    "Rate": 0.16,
                    "Type": "Traslado",
                    "IsRetention": False
                }
            ]
        }
        cfdi_data["Items"].append(item)

    try:
        response = requests.post(
            f"{FACTURAMA_BASE_URL}/3/cfdis",
            json=cfdi_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {
            "error": str(e),
            "detalle": e.response.text if e.response else "No hay respuesta del servidor"
        }


