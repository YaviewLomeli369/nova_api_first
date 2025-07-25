
# --- /home/runner/workspace/facturacion/__init__.py ---



# --- /home/runner/workspace/facturacion/admin.py ---
from django.contrib import admin

# Register your models here.



# --- /home/runner/workspace/facturacion/apps.py ---
from django.apps import AppConfig


class FacturacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'facturacion'



# --- /home/runner/workspace/facturacion/tests.py ---
from django.test import TestCase

# Create your tests here.



# --- /home/runner/workspace/facturacion/views.py ---
from django.shortcuts import render

# Create your views here.



# --- /home/runner/workspace/facturacion/urls.py ---
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from facturacion.views.comprobantes import ComprobanteFiscalViewSet

router = DefaultRouter()
router.register(r'comprobantes', ComprobanteFiscalViewSet, basename='comprobante')

urlpatterns = [
    path('', include(router.urls)),
]



# --- /home/runner/workspace/facturacion/models.py ---
from django.db import models
from core.models import Empresa
from ventas.models import Venta
from accounts.models import Usuario

class ComprobanteFiscal(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('TIMBRADO', 'Timbrado'),
        ('CANCELADO', 'Cancelado'),
        ('ERROR', 'Error'),
    ]

    TIPOS_COMPROBANTE = [
        ('FACTURA', 'Factura'),
        ('NOTA_CREDITO', 'Nota de Crédito'),
        ('RECIBO_NOMINA', 'Recibo de Nómina'),
        # Otros tipos CFDI
    ]
  


    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=36, unique=True, blank=True, null=True)  # UUID timbrado
    # xml = models.TextField(blank=True, null=True)  # XML CFDI completo
    xml = models.FileField(upload_to="cfdi_xmls/", null=True, blank=True)
    pdf = models.FileField(upload_to='cfdi_pdfs/', blank=True, null=True)  # PDF factura
    fecha_timbrado = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')  
    error_mensaje = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_COMPROBANTE, default='FACTURA')
    serie = models.CharField(max_length=10, blank=True, null=True)
    folio = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def esta_timbrado(self):
        return self.estado == 'TIMBRADO' and self.uuid is not None

    class Meta:
      indexes = [
          models.Index(fields=['estado']),
          models.Index(fields=['tipo']),
      ]

  
    def __str__(self):
      venta_id = self.venta.id if self.venta else 'N/A'
      return f"{self.get_tipo_display()} {self.uuid or 'Sin UUID'} - Venta {venta_id}"



# --- /home/runner/workspace/facturacion/migrations/__init__.py ---



# --- /home/runner/workspace/facturacion/migrations/0001_initial.py ---
# Generated by Django 5.2.4 on 2025-07-22 21:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0002_empresa_razon_social'),
        ('ventas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComprobanteFiscal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(blank=True, max_length=36, null=True, unique=True)),
                ('xml', models.TextField(blank=True, null=True)),
                ('pdf', models.FileField(blank=True, null=True, upload_to='cfdi_pdfs/')),
                ('fecha_timbrado', models.DateTimeField(blank=True, null=True)),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('TIMBRADO', 'Timbrado'), ('CANCELADO', 'Cancelado'), ('ERROR', 'Error')], default='PENDIENTE', max_length=20)),
                ('error_mensaje', models.TextField(blank=True, null=True)),
                ('tipo', models.CharField(choices=[('FACTURA', 'Factura'), ('NOTA_CREDITO', 'Nota de Crédito'), ('RECIBO_NOMINA', 'Recibo de Nómina')], default='FACTURA', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.empresa')),
                ('venta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='ventas.venta')),
            ],
            options={
                'indexes': [models.Index(fields=['estado'], name='facturacion_estado_4c1711_idx'), models.Index(fields=['tipo'], name='facturacion_tipo_904fe7_idx')],
            },
        ),
    ]



# --- /home/runner/workspace/facturacion/migrations/0002_comprobantefiscal_folio_comprobantefiscal_serie.py ---
# Generated by Django 5.2.4 on 2025-07-23 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comprobantefiscal',
            name='folio',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='comprobantefiscal',
            name='serie',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]



# --- /home/runner/workspace/facturacion/migrations/0003_alter_comprobantefiscal_folio.py ---
# Generated by Django 5.2.4 on 2025-07-23 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0002_comprobantefiscal_folio_comprobantefiscal_serie'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comprobantefiscal',
            name='folio',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]



# --- /home/runner/workspace/facturacion/serializers/comprobantes.py ---
from rest_framework import serializers
from facturacion.models import ComprobanteFiscal

class ComprobanteFiscalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComprobanteFiscal
        fields = '__all__'
        read_only_fields = [
            'uuid', 'xml', 'pdf', 'fecha_timbrado',
            'estado', 'error_mensaje', 'created_at', 'updated_at'
        ]



# --- /home/runner/workspace/facturacion/serializers/__init__.py ---



# --- /home/runner/workspace/facturacion/views/__init__.py ---



# --- /home/runner/workspace/facturacion/views/comprobantes.py ---
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from facturacion.models import ComprobanteFiscal
from facturacion.serializers.comprobantes import ComprobanteFiscalSerializer
from facturacion.services.timbrado import timbrar_comprobante



class ComprobanteFiscalViewSet(viewsets.ModelViewSet):
    queryset = ComprobanteFiscal.objects.all()
    serializer_class = ComprobanteFiscalSerializer

    @action(detail=True, methods=['post'])
    def timbrar(self, request, pk=None):
        comprobante = self.get_object()
        if comprobante.estado == 'TIMBRADO':
            return Response({"detail": "Comprobante ya timbrado."}, status=status.HTTP_400_BAD_REQUEST)

        comprobante = timbrar_comprobante(comprobante)
        serializer = self.get_serializer(comprobante)
        return Response(serializer.data)


# --- /home/runner/workspace/facturacion/helpers/__init__.py ---



# --- /home/runner/workspace/facturacion/helpers/timbrar_cfdi_venta.py ---
from facturacion.models import ComprobanteFiscal
from facturacion.helpers.facturama import timbrar_cfdi_venta


def procesar_timbrado_venta(venta):
    """
    Timbra una venta usando Facturama y crea el ComprobanteFiscal en DB.
    """
    try:
        cfdi = timbrar_cfdi_venta(venta)

        if "error" in cfdi:
            return ComprobanteFiscal.objects.create(
                empresa=venta.empresa,
                venta=venta,
                estado="ERROR",
                error_mensaje=cfdi["error"],
            )

        comprobante = ComprobanteFiscal.objects.create(
            empresa=venta.empresa,
            venta=venta,
            uuid=cfdi["Complement"]["TimbreFiscalDigital"]["Uuid"],
            xml=cfdi.get("Xml"),
            pdf=cfdi.get("Pdf"),
            serie=cfdi.get("Serie", "A"),
            folio=int(cfdi.get("Folio", 0)),
            estado="TIMBRADO",
            fecha_timbrado=cfdi.get("FechaTimbrado"),
        )
        return comprobante

    except Exception as e:
        return ComprobanteFiscal.objects.create(
            empresa=venta.empresa,
            venta=venta,
            estado="ERROR",
            error_mensaje=str(e),
        )



# --- /home/runner/workspace/facturacion/helpers/facturama.py ---
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


# --- /home/runner/workspace/facturacion/services/procesar.py ---
from facturacion.models import ComprobanteFiscal
from facturacion.helpers.facturama import timbrar_cfdi_venta

def procesar_timbrado_venta(venta):
    try:
        cfdi = timbrar_cfdi_venta(venta)

        if "error" in cfdi:
            return ComprobanteFiscal.objects.create(
                empresa=venta.empresa,
                venta=venta,
                estado="ERROR",
                error_mensaje=cfdi["error"],
            )

        comprobante = ComprobanteFiscal.objects.create(
            empresa=venta.empresa,
            venta=venta,
            uuid=cfdi["Complement"]["TimbreFiscalDigital"]["Uuid"],
            xml=cfdi.get("Xml"),
            pdf=cfdi.get("Pdf"),
            serie=cfdi.get("Serie", "A"),
            folio=int(cfdi.get("Folio", 0)),
            estado="TIMBRADO",
            fecha_timbrado=cfdi.get("FechaTimbrado"),
        )
        return comprobante

    except Exception as e:
        return ComprobanteFiscal.objects.create(
            empresa=venta.empresa,
            venta=venta,
            estado="ERROR",
            error_mensaje=str(e),
        )




# --- /home/runner/workspace/facturacion/services/timbrado.py ---
# facturacion/services/timbrado.py
import datetime
import base64
from django.core.files.base import ContentFile
from facturacion.models import ComprobanteFiscal
from lxml import etree
from datetime import datetime
import requests
from xml.sax.saxutils import escape
from facturacion.utils.sat_firma import firmar_cadena, generar_cadena_original, cargar_certificado_base64
# from facturacion.helpers.facturama import timbrar_cfdi_emision
from facturacion.helpers.facturama import timbrar_cfdi_venta
from facturacion.models import ComprobanteFiscal

def validar_xml(xml_str: str, xsd_path: str):
    xml_doc = etree.fromstring(xml_str.encode('utf-8'))
    with open(xsd_path, 'rb') as f:
        schema_doc = etree.parse(f)
    schema = etree.XMLSchema(schema_doc)
    if not schema.validate(xml_doc):
        errores = [str(e) for e in schema.error_log]
        raise ValueError(f"Errores de validación XML: {errores}")




def guardar_xml_como_archivo(comprobante, contenido_xml: str):
    comprobante.xml.save(f"factura_{comprobante.id}.xml", ContentFile(contenido_xml.encode('utf-8')))



def enviar_a_pac(xml: str, token_api: str) -> dict:
    headers = {
        'Authorization': f'Bearer {token_api}',
        'Content-Type': 'application/xml'
    }
    response = requests.post('https://api.pac.example/timbrar', headers=headers, data=xml.encodea('utf-8'))
    if response.status_code == 200:
        return response.json()
    else:
        try:
            error_json = response.json()
        except Exception:
            error_json = {"detalle": response.text}
        raise Exception(f"Error PAC: {error_json}")
    

def guardar_pdf_base64(comprobante: ComprobanteFiscal, pdf_base64: str):
    """
    Decodifica el PDF y lo guarda como archivo en el modelo.
    """
    if pdf_base64:
        pdf_bytes = base64.b64decode(pdf_base64)
        comprobante.pdf.save(f"factura_{comprobante.id}.pdf",
                             ContentFile(pdf_bytes))

def generar_folio_siguiente(serie="A"):
    ultimo = ComprobanteFiscal.objects.filter(serie=serie).order_by("-folio").first()
    return (ultimo.folio + 1) if ultimo and ultimo.folio else 1


def timbrar_comprobante(comprobante):
    """
    Timbra un comprobante fiscal usando Facturama.
    """
    resultado = timbrar_cfdi_venta()

    if "error" in resultado:
        comprobante.estado = "ERROR"
        comprobante.mensaje_error = resultado["error"]
        comprobante.save()
    else:
        comprobante.estado = "TIMBRADO"
        comprobante.uuid = resultado.get("Complement", {}).get("TimbreFiscalDigital", {}).get("Uuid")
        comprobante.xml_timbrado = resultado.get("Xml")
        comprobante.save()

    return resultado



# --- /home/runner/workspace/facturacion/utils/__init__.py ---



# --- /home/runner/workspace/facturacion/utils/sat_firma.py ---
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


