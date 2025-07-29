from django.urls import path, include
from rest_framework.routers import DefaultRouter
from facturacion.views.comprobantes import TimbrarComprobanteAPIView
# from facturacion.views.comprobantes import ComprobanteFiscalViewSet
from facturacion.views.lista_comprobantes import ComprobanteFiscalListView
router = DefaultRouter()
# router.register(r'comprobantes', ComprobanteFiscalViewSet, basename='comprobante')

urlpatterns = [
    path('', include(router.urls)),
    # path("comprobantes/<int:pk>/timbrar/", TimbrarComprobanteAPIView.as_view(), name="timbrar-comprobante"),
    path('comprobantes/', ComprobanteFiscalListView.as_view(), name='comprobante-fiscal-list')
]
