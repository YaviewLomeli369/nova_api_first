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
            'Accept': 'application/json',
        }
        print(f"DEBUG: Descargando PDF desde: {url}")
        response = requests.get(url, auth=(FACTURAMA_USER, FACTURAMA_PASSWORD), headers=headers)
        print(f"DEBUG: Respuesta PDF - Status: {response.status_code}")
        response.raise_for_status()
        
        # La respuesta es un JSON con el contenido en base64
        response_json = response.json()
        print(f"DEBUG: JSON response keys: {response_json.keys()}")
        
        content_base64 = response_json.get('Content')
        if not content_base64:
            raise Exception("No se encontró el campo 'Content' en la respuesta del PDF")
        
        # Decodificar el contenido base64
        import base64
        pdf_content = base64.b64decode(content_base64)
        print(f"DEBUG: PDF decodificado, tamaño: {len(pdf_content)} bytes")
        return pdf_content

    @staticmethod
    def obtener_xml_por_id(factura_id):
        url = f"https://apisandbox.facturama.mx/api/Cfdi/xml/issued/{factura_id}/"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        print(f"DEBUG: Descargando XML desde: {url}")
        response = requests.get(url, auth=(FACTURAMA_USER, FACTURAMA_PASSWORD), headers=headers)
        print(f"DEBUG: Respuesta XML - Status: {response.status_code}")
        response.raise_for_status()
        
        # La respuesta es un JSON con el contenido en base64
        response_json = response.json()
        print(f"DEBUG: JSON response keys: {response_json.keys()}")
        
        content_base64 = response_json.get('Content')
        if not content_base64:
            raise Exception("No se encontró el campo 'Content' en la respuesta del XML")
        
        # Decodificar el contenido base64
        import base64
        xml_content = base64.b64decode(content_base64)
        print(f"DEBUG: XML decodificado, tamaño: {len(xml_content)} bytes")
        return xml_content


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