from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import base64

def generar_cadena_original(xml_str: str) -> str:
    # En producción usar XSLT SAT (cadenaoriginal_4_0.xslt)
    return xml_str  # Placeholder

def firmar_cadena(cadena_original: str, ruta_llave_privada: str, password: str) -> str:
    with open(ruta_llave_privada, 'rb') as f:
        private_key = RSA.import_key(f.read(), passphrase=password)
    h = SHA256.new(cadena_original.encode('utf-8'))
    signature = pkcs1_15.new(private_key).sign(h)
    return base64.b64encode(signature).decode('utf-8')

def cargar_certificado_base64(ruta_cert: str) -> tuple[str, str]:
    with open(ruta_cert, 'rb') as f:
        cert = f.read()
    cert_b64 = base64.b64encode(cert).decode('utf-8')
    # Número de certificado del SAT (últimos 20 caracteres hex del serial)
    from cryptography import x509
    cert_obj = x509.load_der_x509_certificate(cert)
    serial = format(cert_obj.serial_number, 'x').upper().zfill(20)
    return cert_b64, serial
