from django.urls import path, include
from rest_framework.routers import DefaultRouter
from contabilidad.views.asiento_contable import AsientoContableViewSet
from contabilidad.views.cuenta_contable import CuentaContableViewSet


router = DefaultRouter()
router.register(r'entries', AsientoContableViewSet, basename='asiento')
router.register(r'accounts', CuentaContableViewSet, basename='cuenta_contable')


urlpatterns = [
    path('', include(router.urls)),
]


