
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



# --- /home/runner/workspace/facturacion/models.py ---
from django.db import models
from core.models import Empresa
from ventas.models import Venta
from accounts.models import Usuario
from django.utils import timezone
from django.core.exceptions import ValidationError

class TimbradoLog(models.Model):
    comprobante = models.ForeignKey('ComprobanteFiscal', on_delete=models.CASCADE, related_name='logs_timbrado')
    fecha_intento = models.DateTimeField(default=timezone.now)
    exito = models.BooleanField(default=False)
    mensaje_error = models.TextField(blank=True, null=True)
    uuid_obtenido = models.CharField(max_length=36, blank=True, null=True)
    facturama_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-fecha_intento']

    def __str__(self):
        status = "Éxito" if self.exito else "Error"
        return f"{status} - {self.fecha_intento} - Comprobante {self.comprobante.id}"

class MetodoPagoChoices(models.TextChoices):
    PUE = 'PUE', 'Pago en una sola exhibición'
    PPD = 'PPD', 'Pago en parcialidades o diferido'

# Fuente oficial: Catálogo SAT c_FormaPago vigente al 2025
# https://www.sat.gob.mx/consultas/42930/catalogo-de-forma-de-pago
class FormaPagoChoices(models.TextChoices):
    EFECTIVO = '01', 'Efectivo'
    CHEQUE_NOMINATIVO = '02', 'Cheque nominativo'
    TRANSFERENCIA_ELECTRONICA = '03', 'Transferencia electrónica de fondos'
    TARJETA_CREDITO = '04', 'Tarjeta de crédito'
    MONEDERO_ELECTRONICO = '05', 'Monedero electrónico'
    DINERO_ELECTRONICO = '06', 'Dinero electrónico'
    VALES_DESPENSA = '08', 'Vales de despensa'
    DACION_EN_PAGO = '12', 'Dación en pago'
    PAGO_SUBROGACION = '13', 'Pago por subrogación'
    PAGO_CONSIGNACION = '14', 'Pago por consignación'
    CONDONACION = '15', 'Condonación'
    COMPENSACION = '17', 'Compensación'
    NOVACION = '23', 'Novación'
    CONFUSION = '24', 'Confusión'
    REMISION_DE_DEUDA = '25', 'Remisión de deuda'
    PRESCRIPCION_CADUCIDAD = '26', 'Prescripción o caducidad'
    SATISFACCION_ACREEDOR = '27', 'A satisfacción del acreedor'
    TARJETA_DEBITO = '28', 'Tarjeta de débito'
    TARJETA_SERVICIOS = '29', 'Tarjeta de servicios'
    APLICACION_ANTICIPOS = '30', 'Aplicación de anticipos'
    INTERMEDIARIO_PAGOS = '31', 'Intermediario de pagos'
    POR_DEFINIR = '99', 'Por definir'


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

    reintentos_timbrado = models.PositiveIntegerField(default=0)
    max_reintentos = 3  # Puedes hacerlo campo o constante

    # Opcional: fecha del último intento
    fecha_ultimo_intento = models.DateTimeField(blank=True, null=True)


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
    correo_enviado = models.BooleanField(default=False)  # NUEVO CAMPO
    metodo_pago = models.CharField(
        max_length=3,
        choices=MetodoPagoChoices.choices,
        blank=True,
        null=True,
        help_text="Método de pago según catálogo SAT (PUE, PPD)"
    )
    forma_pago = models.CharField(
        max_length=3,
        choices=FormaPagoChoices.choices,
        blank=True,
        null=True,
        help_text="Forma de pago clave SAT (Ej: 01 Efectivo, 03 Transferencia)"
    )
    exportacion = models.CharField(
        max_length=2, 
        default='01', 
        choices=[
            ('01', 'No aplica'),
            ('02', 'Definitiva'),
            ('03', 'Temporal'),
        ],
        help_text="Exportación según el catálogo SAT c_Exportacion"
    )
    facturama_id = models.CharField(max_length=100, blank=True, null=True)

    motivo_cancelacion = models.CharField(max_length=3, blank=True, null=True, choices=[
        ('01', 'Comprobante emitido con errores con relación'),
        ('02', 'Comprobante emitido con errores sin relación'),
        ('03', 'No se llevó a cabo la operación'),
        ('04', 'Operación nominativa relacionada en la factura global'),
    ])
    sustitucion_uuid = models.CharField(max_length=36, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def esta_timbrado(self):
        return self.estado == 'TIMBRADO' and self.uuid is not None

    def clean(self):
        if self.estado == 'TIMBRADO':
            if not self.metodo_pago:
                raise ValidationError({'metodo_pago': "Requerido al estar timbrado."})
            if not self.forma_pago:
                raise ValidationError({'forma_pago': "Requerido al estar timbrado."})
            if not self.empresa or not self.empresa.rfc:
                raise ValidationError({'empresa': "La empresa debe tener RFC."})
            if not self.venta.cliente.rfc:
                raise ValidationError({'venta': "El cliente debe tener RFC para timbrar."})

    class Meta:
      indexes = [
          models.Index(fields=['estado']),
          models.Index(fields=['tipo']),
      ]

  
    def __str__(self):
      venta_id = self.venta.id if self.venta else 'N/A'
      return f"{self.get_tipo_display()} {self.uuid or 'Sin UUID'} - Venta {venta_id}"



# --- /home/runner/workspace/facturacion/urls.py ---
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from facturacion.views.comprobantes import TimbrarComprobanteAPIView
# from facturacion.views.comprobantes import ComprobanteFiscalViewSet
from facturacion.views.lista_comprobantes import ComprobanteFiscalListView
from facturacion.views.cancelar_factura import cancelar_cfdi
from facturacion.views.validaciones import validar_datos_fiscales_view
# from facturacion.utils.validaciones import validar_datos_fiscales
from facturacion.views.timbrado import TimbradoLogListView
from facturacion.views.vista_previa_factura import vista_previa_pdf


router = DefaultRouter()
# router.register(r'comprobantes', ComprobanteFiscalViewSet, basename='comprobante')

urlpatterns = [
    path('', include(router.urls)),
    # path("comprobantes/<int:pk>/timbrar/", TimbrarComprobanteAPIView.as_view(), name="timbrar-comprobante"),
    path('comprobantes/', ComprobanteFiscalListView.as_view(), name='comprobante-fiscal-list'),
    path('cancelar-cfdi/<str:uuid>/', cancelar_cfdi, name='cancelar_cfdi'),
    path('validar/<int:venta_id>/', validar_datos_fiscales_view, name='validar-datos-fiscales'),
    path('comprobantes/<int:comprobante_id>/logs-timbrado/', TimbradoLogListView.as_view(), name='logs-timbrado'),
    path('comprobantes/<int:pk>/ver-pdf/', vista_previa_pdf, name='vista_previa_pdf'),
]



# --- /home/runner/workspace/facturacion/migrations/__init__.py ---



# --- /home/runner/workspace/facturacion/migrations/0001_initial.py ---
# Generated by Django 5.2.4 on 2025-07-30 17:07

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('ventas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComprobanteFiscal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reintentos_timbrado', models.PositiveIntegerField(default=0)),
                ('fecha_ultimo_intento', models.DateTimeField(blank=True, null=True)),
                ('uuid', models.CharField(blank=True, max_length=36, null=True, unique=True)),
                ('xml', models.FileField(blank=True, null=True, upload_to='cfdi_xmls/')),
                ('pdf', models.FileField(blank=True, null=True, upload_to='cfdi_pdfs/')),
                ('fecha_timbrado', models.DateTimeField(blank=True, null=True)),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('TIMBRADO', 'Timbrado'), ('CANCELADO', 'Cancelado'), ('ERROR', 'Error')], default='PENDIENTE', max_length=20)),
                ('error_mensaje', models.TextField(blank=True, null=True)),
                ('tipo', models.CharField(choices=[('FACTURA', 'Factura'), ('NOTA_CREDITO', 'Nota de Crédito'), ('RECIBO_NOMINA', 'Recibo de Nómina')], default='FACTURA', max_length=20)),
                ('serie', models.CharField(blank=True, max_length=10, null=True)),
                ('folio', models.PositiveIntegerField(blank=True, null=True)),
                ('correo_enviado', models.BooleanField(default=False)),
                ('metodo_pago', models.CharField(blank=True, choices=[('PUE', 'Pago en una sola exhibición'), ('PPD', 'Pago en parcialidades o diferido')], help_text='Método de pago según catálogo SAT (PUE, PPD)', max_length=3, null=True)),
                ('forma_pago', models.CharField(blank=True, choices=[('01', 'Efectivo'), ('02', 'Cheque nominativo'), ('03', 'Transferencia electrónica de fondos'), ('04', 'Tarjeta de crédito'), ('05', 'Monedero electrónico'), ('06', 'Dinero electrónico'), ('08', 'Vales de despensa'), ('12', 'Dación en pago'), ('13', 'Pago por subrogación'), ('14', 'Pago por consignación'), ('15', 'Condonación'), ('17', 'Compensación'), ('23', 'Novación'), ('24', 'Confusión'), ('25', 'Remisión de deuda'), ('26', 'Prescripción o caducidad'), ('27', 'A satisfacción del acreedor'), ('28', 'Tarjeta de débito'), ('29', 'Tarjeta de servicios'), ('30', 'Aplicación de anticipos'), ('31', 'Intermediario de pagos'), ('99', 'Por definir')], help_text='Forma de pago clave SAT (Ej: 01 Efectivo, 03 Transferencia)', max_length=3, null=True)),
                ('exportacion', models.CharField(choices=[('01', 'No aplica'), ('02', 'Definitiva'), ('03', 'Temporal')], default='01', help_text='Exportación según el catálogo SAT c_Exportacion', max_length=2)),
                ('facturama_id', models.CharField(blank=True, max_length=100, null=True)),
                ('motivo_cancelacion', models.CharField(blank=True, choices=[('01', 'Comprobante emitido con errores con relación'), ('02', 'Comprobante emitido con errores sin relación'), ('03', 'No se llevó a cabo la operación'), ('04', 'Operación nominativa relacionada en la factura global')], max_length=3, null=True)),
                ('sustitucion_uuid', models.CharField(blank=True, max_length=36, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.empresa')),
                ('venta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='ventas.venta')),
            ],
        ),
        migrations.CreateModel(
            name='TimbradoLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_intento', models.DateTimeField(default=django.utils.timezone.now)),
                ('exito', models.BooleanField(default=False)),
                ('mensaje_error', models.TextField(blank=True, null=True)),
                ('uuid_obtenido', models.CharField(blank=True, max_length=36, null=True)),
                ('facturama_id', models.CharField(blank=True, max_length=100, null=True)),
                ('comprobante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs_timbrado', to='facturacion.comprobantefiscal')),
            ],
            options={
                'ordering': ['-fecha_intento'],
            },
        ),
        migrations.AddIndex(
            model_name='comprobantefiscal',
            index=models.Index(fields=['estado'], name='facturacion_estado_4c1711_idx'),
        ),
        migrations.AddIndex(
            model_name='comprobantefiscal',
            index=models.Index(fields=['tipo'], name='facturacion_tipo_904fe7_idx'),
        ),
    ]



# --- /home/runner/workspace/facturacion/serializers/__init__.py ---



# --- /home/runner/workspace/facturacion/serializers/comprobante_fiscal.py ---
# serializers.py

from rest_framework import serializers
from facturacion.models import ComprobanteFiscal
from ventas.models import Venta
from accounts.models import Usuario
from core.models import Empresa


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['id', 'nombre', 'rfc']  # Personaliza los campos que quieres incluir

class VentaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)

    class Meta:
        model = Venta
        fields = ['id', 'cliente_nombre']  # Personaliza los campos que quieres incluir

class ComprobanteFiscalSerializer(serializers.ModelSerializer):
    empresa = EmpresaSerializer(read_only=True)  # Relación anidada
    venta = VentaSerializer(read_only=True)  # Relación anidada
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    forma_pago_display = serializers.CharField(source='get_forma_pago_display', read_only=True)

    class Meta:
        model = ComprobanteFiscal
        fields = '__all__'  # También incluye todos los campos del modelo



# --- /home/runner/workspace/facturacion/serializers/timbrado.py ---
from rest_framework import serializers
from facturacion.models import TimbradoLog

class TimbradoLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimbradoLog
        fields = ['id', 'fecha_intento', 'exito', 'mensaje_error', 'uuid_obtenido', 'facturama_id']


# --- /home/runner/workspace/facturacion/views/__init__.py ---



# --- /home/runner/workspace/facturacion/views/comprobantes.py ---
# views/comprobantes.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from facturacion.models import ComprobanteFiscal
from facturacion.utils.build_facturama_payload import build_facturama_payload
from facturacion.services.facturama import FacturamaService

class TimbrarComprobanteAPIView(APIView):
    def post(self, request, pk):
        comprobante = get_object_or_404(ComprobanteFiscal, pk=pk)
        payload = build_facturama_payload(comprobante)

        try:
            respuesta = FacturamaService.timbrar_comprobante(payload)
            # Aquí podrías guardar en el comprobante la respuesta o UUID recibido
            return Response(respuesta, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# --- /home/runner/workspace/facturacion/views/lista_comprobantes.py ---
# views.py

from rest_framework import generics
from facturacion.models import ComprobanteFiscal
from facturacion.serializers.comprobante_fiscal import ComprobanteFiscalSerializer
from rest_framework.permissions import IsAuthenticated

class ComprobanteFiscalListView(generics.ListAPIView):
    queryset = ComprobanteFiscal.objects.all()
    serializer_class = ComprobanteFiscalSerializer
    permission_classes = [IsAuthenticated]

    # Filtros, puedes adaptarlo a tus necesidades
    def get_queryset(self):
        queryset = super().get_queryset()
        # Aquí puedes agregar filtros, por ejemplo, por estado o tipo de comprobante
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset



# --- /home/runner/workspace/facturacion/views/cancelar_factura.py ---
import requests
import base64
from django.utils.timezone import now
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from facturacion.models import ComprobanteFiscal
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# facturacion/views.py

@csrf_exempt
def cancelar_cfdi(request, uuid):
    try:
        cfdi = ComprobanteFiscal.objects.get(uuid=uuid)
    except ComprobanteFiscal.DoesNotExist:
        return JsonResponse({"error": "CFDI no encontrado"}, status=404)

    if cfdi.estado == 'CANCELADO':
        return JsonResponse({"message": "El CFDI ya fue cancelado"}, status=400)

    # Validar que tengas el ID de Facturama (no UUID)
    factura_id = getattr(cfdi, 'facturama_id', None)
    if not factura_id:
        return JsonResponse({"error": "No se encontró el ID de Facturama en el comprobante."}, status=400)

    # Parámetros requeridos
    motive = cfdi.motivo_cancelacion or "02"
    uuid_replacement = cfdi.sustitucion_uuid or ""
    cancel_type = "issued"  # o "Received" dependiendo del rol; normalmente "Issued"

    # Autenticación básica
    api_key = f'{settings.FACTURAMA_USER}:{settings.FACTURAMA_PASSWORD}'
    api_key_encoded = base64.b64encode(api_key.encode()).decode()
    headers = {
        "Authorization": f"Basic {api_key_encoded}",
        "Content-Type": "application/json"
    }

    url = f'https://apisandbox.facturama.mx/cfdi/{factura_id}?type={cancel_type}&motive={motive}&uuidReplacement={uuid_replacement}'

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        cfdi.estado = 'CANCELADO'
        cfdi.fecha_cancelacion = now()
        cfdi.save()
        return JsonResponse({"message": "CFDI cancelado correctamente"})
    else:
        try:
            detalles = response.json()
        except Exception:
            detalles = response.text or {}
        return JsonResponse({
            "error": "Error al cancelar CFDI",
            "status_code": response.status_code,
            "detalles": detalles
        }, status=400)

# import requests
# import base64
# from django.utils.timezone import now
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from facturacion.models import ComprobanteFiscal
# from django.conf import settings


# @csrf_exempt
# def cancelar_cfdi(request, uuid):
#     if request.method != 'POST':
#         return JsonResponse({"error": "Método no permitido"}, status=405)

#     try:
#         cfdi = ComprobanteFiscal.objects.get(uuid=uuid)
#     except ComprobanteFiscal.DoesNotExist:
#         return JsonResponse({"error": "CFDI no encontrado"}, status=404)

#     if cfdi.estado == 'CANCELADO':
#         return JsonResponse({"message": "El CFDI ya fue cancelado"}, status=400)

#     # ⚙️ Parámetros obligatorios
#     cfdi_id = cfdi.cfdi_id  # Este es el ID interno de Facturama, no el UUID fiscal
#     type_ = "issued"
#     motive = cfdi.motivo_cancelacion or "02"
#     uuid_replacement = cfdi.sustitucion_uuid or ""

#     # 🔒 Autenticación
#     api_key = f'{settings.FACTURAMA_USER}:{settings.FACTURAMA_PASSWORD}'
#     api_key_encoded = base64.b64encode(api_key.encode()).decode()

#     headers = {
#         "Authorization": f"Basic {api_key_encoded}"
#     }

#     url = f"https://apisandbox.facturama.mx/cfdi/{cfdi_id}?type={type_}&motive={motive}&uuidReplacement={uuid_replacement}"

#     response = requests.delete(url, headers=headers)

#     if response.status_code == 200:
#         data = response.json()

#         cfdi.estado = 'CANCELADO'
#         cfdi.fecha_cancelacion = now()
#         cfdi.acuse_cancelacion_xml = data.get("AcuseXmlBase64", "")
#         cfdi.save()

#         return JsonResponse({
#             "message": "CFDI cancelado correctamente",
#             "status": data.get("Status"),
#             "uuid": data.get("Uuid"),
#             "acuse_xml": data.get("AcuseXmlBase64", "")
#         })

#     try:
#         error_data = response.json()
#     except ValueError:
#         error_data = {}

#     return JsonResponse({
#         "error": "Error al cancelar CFDI",
#         "status_code": response.status_code,
#         "detalles": error_data
#     }, status=response.status_code)




# --- /home/runner/workspace/facturacion/views/validaciones.py ---
# facturacion/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from facturacion.utils.validaciones import validar_datos_fiscales
from facturacion.models import ComprobanteFiscal

@api_view(['GET'])
def validar_datos_fiscales_view(request, venta_id):
    try:
        comprobante = ComprobanteFiscal.objects.get(venta_id=venta_id)
    except ComprobanteFiscal.DoesNotExist:
        return Response({"error": "Comprobante no encontrado para esta venta"}, status=404)

    resultado = validar_datos_fiscales(comprobante)
    if resultado["ok"]:
        return Response({"ok": True, "mensaje": "Todos los datos fiscales son válidos"})
    else:
        return Response({"ok": False, "errores": resultado["errores"]}, status=400)



# --- /home/runner/workspace/facturacion/views/reintentar_timbrado.py ---
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from facturacion.models import ComprobanteFiscal
from facturacion.services.timbrado_helpers import intentar_timbrado_comprobante
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reintentar_timbrado(request, comprobante_id):
    try:
        comprobante = ComprobanteFiscal.objects.get(id=comprobante_id)
    except ComprobanteFiscal.DoesNotExist:
        return Response({"error": "Comprobante no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if comprobante.estado == 'TIMBRADO':
        return Response({"message": "Comprobante ya está timbrado."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        intentar_timbrado_comprobante(comprobante)
        return Response({"message": "Timbrado exitoso.", "uuid": comprobante.uuid})
    except Exception as e:
        return Response({"error": f"Error al timbrar: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)



# --- /home/runner/workspace/facturacion/views/timbrado.py ---
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from facturacion.models import ComprobanteFiscal, TimbradoLog
from facturacion.serializers.timbrado import TimbradoLogSerializer
from rest_framework.exceptions import NotFound

class TimbradoLogListView(generics.ListAPIView):
    serializer_class = TimbradoLogSerializer
    permission_classes = [IsAuthenticated]  # o déjalo abierto si quieres

    def get_queryset(self):
        comprobante_id = self.kwargs.get('comprobante_id')
        try:
            comprobante = ComprobanteFiscal.objects.get(id=comprobante_id)
        except ComprobanteFiscal.DoesNotExist:
            raise NotFound("Comprobante no encontrado")

        return comprobante.logs_timbrado.all()



# --- /home/runner/workspace/facturacion/views/vista_previa_factura.py ---
from django.http import FileResponse, Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from facturacion.models import ComprobanteFiscal

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def vista_previa_pdf(request, pk):
    try:
        comprobante = ComprobanteFiscal.objects.get(pk=pk)
        if not comprobante.pdf or not comprobante.pdf.path:
            raise Http404("PDF no disponible.")
        return FileResponse(open(comprobante.pdf.path, 'rb'), content_type='application/pdf')
    except ComprobanteFiscal.DoesNotExist:
        raise Http404("Comprobante no encontrado.")


# --- /home/runner/workspace/facturacion/services/facturama.py ---
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


# --- /home/runner/workspace/facturacion/services/timbrado_helpers.py ---
from django.utils import timezone
from facturacion.models import ComprobanteFiscal
from facturacion.services.facturama import FacturamaService
from facturacion.utils.build_facturama_payload import build_facturama_payload
from facturacion.utils.guardar_archivo_base64 import guardar_archivo_base64
from facturacion.utils.descargar_archivo_por_id import  descargar_archivo_por_id
from facturacion.utils.validaciones import validar_datos_fiscales
from facturacion.utils.enviar_correo import enviar_cfdi_por_correo


from django.utils import timezone
from facturacion.models import ComprobanteFiscal, TimbradoLog
from facturacion.services.facturama import FacturamaService
from facturacion.utils.build_facturama_payload import build_facturama_payload
from facturacion.utils.guardar_archivo_base64 import guardar_archivo_base64
from facturacion.utils.descargar_archivo_por_id import descargar_archivo_por_id
from facturacion.utils.validaciones import validar_datos_fiscales

def intentar_timbrado_comprobante(comprobante: ComprobanteFiscal, max_reintentos=3):
    # Sincronizar método y forma de pago desde venta
    comprobante.metodo_pago = comprobante.venta.metodo_pago or "PUE"
    comprobante.forma_pago = comprobante.venta.forma_pago or "01"
    comprobante.save()

    errores = validar_datos_fiscales(comprobante)
    if not errores["ok"]:
        raise Exception(f"Errores fiscales: {errores['errores']}")

    if comprobante.estado == 'TIMBRADO':
        return comprobante  # Ya está timbrado

    if comprobante.reintentos_timbrado >= max_reintentos:
        raise Exception(f"Máximo de {max_reintentos} reintentos alcanzado para el comprobante {comprobante.id}")

    payload = build_facturama_payload(comprobante)

    try:
        respuesta = FacturamaService.timbrar_comprobante(payload)

        uuid = respuesta.get('Complement', {}).get('TaxStamp', {}).get('Uuid')
        factura_id = respuesta.get('Id')

        comprobante.uuid = uuid
        comprobante.facturama_id = factura_id
        comprobante.estado = 'TIMBRADO'
        comprobante.fecha_timbrado = timezone.now()
        comprobante.error_mensaje = None
        comprobante.reintentos_timbrado += 1
        comprobante.fecha_ultimo_intento = timezone.now()

        xml_base64 = respuesta.get('Xml')
        if xml_base64:
            guardar_archivo_base64(xml_base64, comprobante, tipo='xml')
        elif factura_id:
            descargar_archivo_por_id(factura_id, comprobante, formato='xml')

        pdf_base64 = respuesta.get('Pdf')
        if pdf_base64:
            guardar_archivo_base64(pdf_base64, comprobante, tipo='pdf')
        elif factura_id:
            descargar_archivo_por_id(factura_id, comprobante, formato='pdf')

        comprobante.save()

        # Guardar registro de log de éxito
        TimbradoLog.objects.create(
            comprobante=comprobante,
            fecha_intento=timezone.now(),
            exito=True,
            mensaje_error=None,
            uuid_obtenido=uuid,
            facturama_id=factura_id,
        )

        # Enviar correo con CFDI adjunto
        try:
            cliente_email = comprobante.venta.cliente.correo
            cliente_email_2 = "yaview.lomeli@gmail.com"

            if cliente_email:
                enviar_cfdi_por_correo(cliente_email, comprobante)
                enviar_cfdi_por_correo(cliente_email_2, comprobante)

        except Exception as e:
            # Solo loguea el error, no interrumpas el flujo
            print(f"Error enviando correo: {e}")

        return comprobante

    except Exception as e:
        comprobante.estado = 'ERROR'
        comprobante.error_mensaje = str(e)
        comprobante.reintentos_timbrado += 1
        comprobante.fecha_ultimo_intento = timezone.now()
        comprobante.save()

        # Guardar registro de log de error
        TimbradoLog.objects.create(
            comprobante=comprobante,
            fecha_intento=timezone.now(),
            exito=False,
            mensaje_error=str(e),
            uuid_obtenido=None,
            facturama_id=None,
        )

        raise e
# def intentar_timbrado_comprobante(comprobante: ComprobanteFiscal, max_reintentos=3):
#     # Sincronizar método y forma de pago desde venta
#     comprobante.metodo_pago = comprobante.venta.metodo_pago or "PUE"
#     comprobante.forma_pago = comprobante.venta.forma_pago or "01"
#     comprobante.save()

#     errores = validar_datos_fiscales(comprobante)
#     if not errores["ok"]:
#         raise Exception(f"Errores fiscales: {errores['errores']}")

#     if comprobante.estado == 'TIMBRADO':
#         return comprobante  # Ya está timbrado

#     if comprobante.reintentos_timbrado >= max_reintentos:
#         raise Exception(f"Máximo de {max_reintentos} reintentos alcanzado para el comprobante {comprobante.id}")

#     payload = build_facturama_payload(comprobante)

#     try:
#         respuesta = FacturamaService.timbrar_comprobante(payload)

#         uuid = respuesta.get('Complement', {}).get('TaxStamp', {}).get('Uuid')
#         factura_id = respuesta.get('Id')

#         comprobante.uuid = uuid
#         comprobante.facturama_id = factura_id
#         comprobante.estado = 'TIMBRADO'
#         comprobante.fecha_timbrado = timezone.now()
#         comprobante.error_mensaje = None
#         comprobante.reintentos_timbrado += 1
#         comprobante.fecha_ultimo_intento = timezone.now()

#         xml_base64 = respuesta.get('Xml')
#         if xml_base64:
#             guardar_archivo_base64(xml_base64, comprobante, tipo='xml')
#         elif factura_id:
#             descargar_archivo_por_id(factura_id, comprobante, formato='xml')

#         pdf_base64 = respuesta.get('Pdf')
#         if pdf_base64:
#             guardar_archivo_base64(pdf_base64, comprobante, tipo='pdf')
#         elif factura_id:
#             descargar_archivo_por_id(factura_id, comprobante, formato='pdf')

#         comprobante.save()

#         # Guardar registro de log de éxito
#         TimbradoLog.objects.create(
#             comprobante=comprobante,
#             fecha_intento=timezone.now(),
#             exito=True,
#             mensaje_error=None,
#             uuid_obtenido=uuid,
#             facturama_id=factura_id,
#         )

#         return comprobante

#     except Exception as e:
#         comprobante.estado = 'ERROR'
#         comprobante.error_mensaje = str(e)
#         comprobante.reintentos_timbrado += 1
#         comprobante.fecha_ultimo_intento = timezone.now()
#         comprobante.save()

#         # Guardar registro de log de error
#         TimbradoLog.objects.create(
#             comprobante=comprobante,
#             fecha_intento=timezone.now(),
#             exito=False,
#             mensaje_error=str(e),
#             uuid_obtenido=None,
#             facturama_id=None,
#         )

#         raise e



# def intentar_timbrado_comprobante(comprobante: ComprobanteFiscal, max_reintentos=3):
#     # Sincronizar método y forma de pago desde venta
#     comprobante.metodo_pago = comprobante.venta.metodo_pago or "PUE"
#     comprobante.forma_pago = comprobante.venta.forma_pago or "01"
#     comprobante.save()

#     errores = validar_datos_fiscales(comprobante)
#     if not errores["ok"]:
#         raise Exception(f"Errores fiscales: {errores['errores']}")

#     if comprobante.estado == 'TIMBRADO':
#         return comprobante  # Ya está timbrado

#     if comprobante.reintentos_timbrado >= max_reintentos:
#         raise Exception(f"Máximo de {max_reintentos} reintentos alcanzado para el comprobante {comprobante.id}")

#     payload = build_facturama_payload(comprobante)

#     try:
#         respuesta = FacturamaService.timbrar_comprobante(payload)

#         uuid = respuesta.get('Complement', {}).get('TaxStamp', {}).get('Uuid')
#         factura_id = respuesta.get('Id')

#         comprobante.uuid = uuid
#         comprobante.facturama_id = factura_id
#         comprobante.estado = 'TIMBRADO'
#         comprobante.fecha_timbrado = timezone.now()
#         comprobante.error_mensaje = None
#         comprobante.reintentos_timbrado += 1
#         comprobante.fecha_ultimo_intento = timezone.now()

#         xml_base64 = respuesta.get('Xml')
#         if xml_base64:
#             guardar_archivo_base64(xml_base64, comprobante, tipo='xml')
#         elif factura_id:
#             descargar_archivo_por_id(factura_id, comprobante, formato='xml')

#         pdf_base64 = respuesta.get('Pdf')
#         if pdf_base64:
#             guardar_archivo_base64(pdf_base64, comprobante, tipo='pdf')
#         elif factura_id:
#             descargar_archivo_por_id(factura_id, comprobante, formato='pdf')

#         comprobante.save()
#         return comprobante

#     except Exception as e:
#         comprobante.estado = 'ERROR'
#         comprobante.error_mensaje = str(e)
#         comprobante.reintentos_timbrado += 1
#         comprobante.fecha_ultimo_intento = timezone.now()
#         comprobante.save()
#         raise e




# --- /home/runner/workspace/facturacion/utils/__init__.py ---



# --- /home/runner/workspace/facturacion/utils/validaciones.py ---
# facturacion/utils/validaciones.py

import re

def validar_rfc(rfc):
    return bool(re.match(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$", rfc or ""))

def validar_clave_unidad(clave):
    return bool(re.match(r"^[A-Z0-9]{1,5}$", clave or ""))

def validar_datos_fiscales(comprobante):
    errores = {}

    cliente = comprobante.venta.cliente
    empresa = comprobante.empresa
    detalles = comprobante.venta.detalles.all()

    # Cliente
    cliente_errores = {}
    if not validar_rfc(cliente.rfc):
        cliente_errores['rfc'] = "RFC inválido o ausente"
    if not cliente.direccion_codigo_postal:
        cliente_errores['direccion_codigo_postal'] = "Código postal faltante"
    if not cliente.uso_cfdi:
        cliente_errores['uso_cfdi'] = "Uso CFDI no definido"

    if cliente_errores:
        errores['cliente'] = cliente_errores

    # Empresa
    empresa_errores = {}
    if not empresa.rfc or not validar_rfc(empresa.rfc):
        empresa_errores['rfc'] = "RFC inválido o ausente"
    if not empresa.regimen_fiscal:
        empresa_errores['regimen_fiscal'] = "Régimen fiscal faltante"

    if empresa_errores:
        errores['empresa'] = empresa_errores

    # Productos
    productos_errores = []
    for d in detalles:
        p = d.producto
        if not p.clave_sat:
            productos_errores.append({
                "id": p.id,
                "error": "Producto sin clave SAT"
            })
        if not p.unidad_medida or not validar_clave_unidad(p.unidad_medida.clave):
            productos_errores.append({
                "id": p.id,
                "error": "Unidad de medida ausente o inválida"
            })

    if productos_errores:
        errores['productos'] = productos_errores

    # Método y forma de pago
    if not comprobante.metodo_pago:
        errores['metodo_pago'] = "Método de pago no definido"
    if not comprobante.forma_pago:
        errores['forma_pago'] = "Forma de pago no definida"

    if errores:
        return {"ok": False, "errores": errores}
    return {"ok": True}



# --- /home/runner/workspace/facturacion/utils/guardar_archivo_base64.py ---
import base64
from django.core.files.base import ContentFile


def guardar_archivo_base64(base64_str, comprobante, tipo='xml'):
    """
    Guarda un archivo base64 (XML o PDF) en el campo del comprobante correspondiente.
    """
    try:
        decoded_data = base64.b64decode(base64_str)

        if tipo == 'xml':
            comprobante.xml.save(f'cfdi_{comprobante.id}.xml', ContentFile(decoded_data), save=False)
        elif tipo == 'pdf':
            comprobante.pdf.save(f'cfdi_{comprobante.id}.pdf', ContentFile(decoded_data), save=False)
        else:
            raise ValueError("Tipo de archivo no soportado")

    except Exception as e:
        raise Exception(f"Error al guardar archivo {tipo} desde base64: {str(e)}")



# --- /home/runner/workspace/facturacion/utils/descargar_archivo_por_id.py ---
from django.core.files.base import ContentFile
from facturacion.services.facturama import FacturamaService


def descargar_archivo_por_id(factura_id, comprobante, formato='xml'):
    """
    Descarga el XML o PDF desde Facturama usando el ID de la factura.
    """
    try:
        if formato == 'xml':
            archivo_data = FacturamaService.obtener_xml_por_id(factura_id)
            comprobante.xml.save(f'cfdi_{comprobante.id}.xml', ContentFile(archivo_data), save=False)

        elif formato == 'pdf':
            archivo_data = FacturamaService.obtener_pdf_por_id(factura_id)
            comprobante.pdf.save(f'cfdi_{comprobante.id}.pdf', ContentFile(archivo_data), save=False)

        else:
            raise ValueError("Formato no soportado (solo 'xml' o 'pdf')")

    except Exception as e:
        raise Exception(f"Error al descargar archivo {formato} por ID: {str(e)}")



# --- /home/runner/workspace/facturacion/utils/facturama_helpers.py ---
def tipo_cfdi_desde_tipo_comprobante(tipo):
  """
  Convierte el tipo interno del comprobante ('FACTURA', 'NOTA_CREDITO', etc.)
  al tipo de CFDI que Facturama espera: 'I', 'E', 'N', etc.
  """
  mapeo = {
      "FACTURA": "I",           # Ingreso
      "NOTA_CREDITO": "E",      # Egreso
      "RECIBO_NOMINA": "N",     # Nómina
  }
  return mapeo.get(tipo, "I")  # Valor por defecto: Ingreso



# --- /home/runner/workspace/facturacion/utils/enviar_correo.py ---
from django.core.mail import EmailMessage
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

def enviar_cfdi_por_correo(email_destino, comprobante):
    """
    Envía el CFDI (PDF + XML) como adjuntos al email del cliente.
    """
    if not email_destino:
        raise ValueError("El cliente no tiene un correo electrónico válido.")

    asunto = f"Factura electrónica {comprobante.serie or ''}-{comprobante.folio or ''}".strip("- ")
    cuerpo = (
        f"Estimado cliente,\n\nAdjuntamos su factura electrónica.\n\n"
        f"Gracias por su preferencia.\n\nSaludos,\nNova ERP"
    )

    email = EmailMessage(
        asunto,
        cuerpo,
        settings.DEFAULT_FROM_EMAIL,
        [email_destino],
    )

    try:
        # Adjuntar PDF leyendo contenido directamente
        if comprobante.pdf and comprobante.pdf.path and os.path.exists(comprobante.pdf.path):
            with open(comprobante.pdf.path, 'rb') as f:
                email.attach(f'cfdi_{comprobante.id}.pdf', f.read(), 'application/pdf')
        else:
            logger.warning(f"Archivo PDF no encontrado para comprobante {comprobante.id}")

        # Adjuntar XML leyendo contenido directamente
        if comprobante.xml and comprobante.xml.path and os.path.exists(comprobante.xml.path):
            with open(comprobante.xml.path, 'rb') as f:
                email.attach(f'cfdi_{comprobante.id}.xml', f.read(), 'application/xml')
        else:
            logger.warning(f"Archivo XML no encontrado para comprobante {comprobante.id}")

        email.send(fail_silently=False)
        logger.info(f"Correo enviado a {email_destino} con comprobante {comprobante.id}")

        # 🔥 Marcar como enviado si todo fue bien
        comprobante.correo_enviado = True
        comprobante.save(update_fields=['correo_enviado'])

    except Exception as e:
        logger.error(f"Error enviando correo con comprobante {comprobante.id}: {e}")
        raise



# --- /home/runner/workspace/facturacion/utils/build_facturama_payload.py ---
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
    # print("Payload que se enviará a Facturama:")
    # print(json.dumps(payload, indent=4, ensure_ascii=False))


    return payload


