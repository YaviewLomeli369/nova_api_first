# services/facturama.py
import requests
from requests.auth import HTTPBasicAuth

FACTURAMA_API_URL = "https://api.facturama.mx/3/cfdi"  # Endpoint para timbrar
FACTURAMA_USER = "tu_usuario"  # Aquí va el RFC o usuario Facturama
FACTURAMA_PASSWORD = "tu_password"  # Aquí va la contraseña/token Facturama

class FacturamaService:
    @staticmethod
    def timbrar_comprobante(payload: dict):
        url = FACTURAMA_API_URL
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        response = requests.post(
            url,
            json=payload,
            auth=HTTPBasicAuth(FACTURAMA_USER, FACTURAMA_PASSWORD),
            headers=headers,
            timeout=30,
        )

        return FacturamaService.handle_response(response)

    @staticmethod
    def handle_response(response):
        if response.status_code == 201:
            # Timbrado exitoso
            return response.json()
        else:
            # Algo falló, puedes loggear o levantar excepción
            raise Exception(
                f"Error al timbrar: {response.status_code} - {response.text}"
            )