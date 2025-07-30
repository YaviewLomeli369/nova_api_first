import requests
from django.conf import settings

def consultar_estado_cfdi(uuid: str, issuer_rfc: str, receiver_rfc: str, total: float) -> dict:
    url = f"https://apisandbox.facturama.mx/cfdi/status"
    headers = {
        "Authorization": f"Basic {settings.FACTURAMA_CREDENTIALS}"
    }
    params = {
        "uuid": uuid,
        "issuerRfc": issuer_rfc,
        "receiverRfc": receiver_rfc,
        "total": f"{total:.2f}"  # asegura formato decimal con dos decimales
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error al consultar estado CFDI: {response.text}")