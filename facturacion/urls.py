from django.urls import path, include
from rest_framework.routers import DefaultRouter
from facturacion.views.comprobantes import TimbrarComprobanteAPIView
# from facturacion.views.comprobantes import ComprobanteFiscalViewSet
from facturacion.views.lista_comprobantes import ComprobanteFiscalListView
from facturacion.views.cancelar_factura import cancelar_cfdi
from facturacion.views.validaciones import validar_datos_fiscales_view
from facturacion.utils.validaciones import validar_datos_fiscales

router = DefaultRouter()
# router.register(r'comprobantes', ComprobanteFiscalViewSet, basename='comprobante')

urlpatterns = [
    path('', include(router.urls)),
    # path("comprobantes/<int:pk>/timbrar/", TimbrarComprobanteAPIView.as_view(), name="timbrar-comprobante"),
    path('comprobantes/', ComprobanteFiscalListView.as_view(), name='comprobante-fiscal-list'),
    path('cancelar-cfdi/<str:uuid>/', cancelar_cfdi, name='cancelar_cfdi'),
    path('validar/<int:venta_id>/', validar_datos_fiscales_view, name='validar-datos-fiscales'),
]
