# services/facturama.py
# from django.conf import Settings
from django.conf import settings   # correcto
import requests
from requests.auth import HTTPBasicAuth

# FACTURAMA_API_URL = "https://api.facturama.mx/3/cfdi"  # Endpoint para timbrar
FACTURAMA_API_URL = settings.FACTURAMA_API_URL
FACTURAMA_USER = settings.FACTURAMA_USER  # Aquí va el RFC o usuario Facturama
FACTURAMA_PASSWORD = settings.FACTURAMA_PASSWORD  # Aquí va la contraseña/token Facturama

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


    # https://apisandbox.facturama.mx/api/Cfdi/xml/issued/4kxSOfZWU95PfTaUF4xmnw2/


    @staticmethod
    def obtener_pdf_por_id(factura_id):
        url = f"https://apisandbox.facturama.mx/api/Cfdi/pdf/issued/{factura_id}/"
        headers = {
            'Content-Type': 'application/json',
        }
        print(f"DEBUG: Descargando PDF desde: {url}")
        response = requests.get(url, auth=(FACTURAMA_USER, FACTURAMA_PASSWORD), headers=headers)
        print(f"DEBUG: Respuesta PDF - Status: {response.status_code}, Content-Length: {len(response.content)}")
        response.raise_for_status()
        return response.content

    @staticmethod
    def obtener_xml_por_id(factura_id):
        url = f"https://apisandbox.facturama.mx/api/Cfdi/xml/issued/{factura_id}/"
        headers = {
            'Accept': 'application/xml',
        }
        print(f"DEBUG: Descargando XML desde: {url}")
        response = requests.get(url, auth=(FACTURAMA_USER, FACTURAMA_PASSWORD), headers=headers)
        print(f"DEBUG: Respuesta XML - Status: {response.status_code}, Content-Length: {len(response.content)}")
        response.raise_for_status()
        return response.content


    # @staticmethod
    # def obtener_pdf_por_id(factura_id):
    #     url = f"https://apisandbox.facturama.mx/3/cfdi/{factura_id}/"
    #     headers = {
    #         'Content-Type': 'application/json',
    #     }
    #     response = requests.get(url, auth=(FACTURAMA_USER, FACTURAMA_PASSWORD), headers=headers)
    #     response.raise_for_status()
    #     return response.content

    # @staticmethod
    # def obtener_xml_por_id(factura_id):
    #     url = f"https://apisandbox.facturama.mx/3/cfdi/{factura_id}/"
    #     headers = {
    #         'Accept': 'application/xml',
    #     }
    #     response = requests.get(url, auth=(FACTURAMA_USER, FACTURAMA_PASSWORD), headers=headers)
    #     response.raise_for_status()
    #     return response.content