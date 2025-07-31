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
from facturacion.views.vista_previa_xml import vista_previa_xml
from facturacion.views.reintentar_timbrado import reintentar_timbrado
from facturacion.views.comprobante_fiscal import ComprobanteFiscalViewSet
from facturacion.views.acuses import descargar_acuse_cancelacion
from facturacion.views.reenviar_email_cfdi import reenviar_email_cfdi
from facturacion.views.envio_cfdi_viewset import EnvioCorreoCFDIViewSet

router = DefaultRouter()
# router.register(r'comprobantes', ComprobanteFiscalViewSet, basename='comprobante')
router.register(r'comprobantes', ComprobanteFiscalViewSet, basename='comprobantes')
router.register(r'envios', EnvioCorreoCFDIViewSet, basename='envios-cfdi')

urlpatterns = [
    path('', include(router.urls)),
    # path("comprobantes/<int:pk>/timbrar/", TimbrarComprobanteAPIView.as_view(), name="timbrar-comprobante"),
    path('comprobantes/', ComprobanteFiscalListView.as_view(), name='comprobante-fiscal-list'),
    path('cancelar-cfdi/<str:uuid>/', cancelar_cfdi, name='cancelar_cfdi'),
    path('validar/<int:venta_id>/', validar_datos_fiscales_view, name='validar-datos-fiscales'),
    path('comprobantes/<int:comprobante_id>/logs-timbrado/', TimbradoLogListView.as_view(), name='logs-timbrado'),
    path('comprobantes/<int:pk>/ver-pdf/', vista_previa_pdf, name='vista_previa_pdf'),
    path('comprobantes/<int:pk>/vista-previa-xml/', vista_previa_xml, name='vista_previa_xml'),
    path('comprobantes/<int:comprobante_id>/reintentar/', reintentar_timbrado, name='reintentar_timbrado'),
    path('comprobantes/<uuid:uuid>/acuse-cancelacion/', descargar_acuse_cancelacion, name='descargar_acuse_cancelacion'),
    path('comprobantes/<str:uuid>/reenviar-email/', reenviar_email_cfdi, name='reenviar_email_cfdi'),
]



