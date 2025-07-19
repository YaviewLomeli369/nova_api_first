from rest_framework.routers import DefaultRouter
from finanzas.views.cuentas_por_cobrar import  CuentaPorCobrarViewSet 
from finanzas.views.cuentas_por_pagar import CuentaPorPagarViewSet
from finanzas.views.pagos import  PagoViewSet


router = DefaultRouter()
router.register(r'cuentas_por_pagar', CuentaPorPagarViewSet, basename='cuentas_por_pagar')
router.register(r'cuentas_por_cobrar', CuentaPorCobrarViewSet, basename='cuentas_por_cobrar')
router.register(r'pagos', PagoViewSet, basename='pagos')

urlpatterns = router.urls