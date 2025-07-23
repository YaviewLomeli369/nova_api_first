import requests
import base64
from datetime import datetime
from django.conf import settings
from datetime import datetime

FACTURAMA_BASE_URL = "https://apisandbox.facturama.mx"

def timbrar_cfdi_prueba():
    user_pass = f"{settings.FACTURAMA_USER}:{settings.FACTURAMA_PASSWORD}"
    encoded_credentials = base64.b64encode(user_pass.encode()).decode()
    print("Authorization header:", f"Basic {encoded_credentials}")
    
    print("Entrando a timbrar_cfdi_prueba")
    user_pass = f"{settings.FACTURAMA_USER}:{settings.FACTURAMA_PASSWORD}"
    token = base64.b64encode(user_pass.encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

    print("Authorization header:", headers["Authorization"])

    # Datos CFDI - mínimos, válidos y sin redundancias
    cfdi_data = {
        "Serie": "A",
        "Folio": "1003",
        "Fecha": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        "PaymentForm": "01",           # Forma de pago, obligatoria
        "CondicionesDePago": "Contado",
        "SubTotal": 100.00,
        "Descuento": 0.00,
        "Moneda": "MXN",
        "Total": 116.00,
        "CfdiType": "I",               # Tipo de comprobante
        "PaymentMethod": "PUE",        # Método de pago
        "ExpeditionPlace": "64000",    # Lugar de expedición (CP)
        "Receiver": {
            "Rfc": "XAXX010101000",
            "Name": "PUBLICO EN GENERAL",
            "CfdiUse": "S01",
            "FiscalRegime": "616",      # Régimen fiscal (obligatorio)
            "TaxZipCode": "64000"       # Código postal receptor (obligatorio)
        },
        "Conceptos": [
            {
                "ClaveProdServ": "01010101",
                "Cantidad": 1,
                "ClaveUnidad": "ACT",
                "Descripcion": "Producto de Prueba",
                "ValorUnitario": 100.00,
                "Importe": 100.00,
                "Descuento": 0.00,
                "ObjetoImp": "01"  # Objeto del impuesto (clave catálogo c_ObjetoImp)
                # **No incluir campo Impuestos o Taxes aquí**
            }
        ],
        "Impuestos": {
            "Traslados": [
                {
                    "Impuesto": "002",       # IVA
                    "TipoFactor": "Tasa",
                    "TasaOCuota": 0.160000,
                    "Importe": 16.00
                }
            ]
        }
    }

    try:
        response = requests.post(
            f"{FACTURAMA_BASE_URL}/3/cfdis",
            json=cfdi_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("Status code:", e.response.status_code)
        print("Response text:", e.response.text)
        return {"error": str(e), "detalle": e.response.text}
