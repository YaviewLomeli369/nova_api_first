from django.urls import path, include
from rest_framework.routers import DefaultRouter
from facturacion.views.comprobantes import ComprobanteFiscalViewSet

router = DefaultRouter()
router.register(r'comprobantes', ComprobanteFiscalViewSet, basename='comprobante')

urlpatterns = [
    path('', include(router.urls)),
]
