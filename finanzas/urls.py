# finanzas/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from finanzas.views.cuentas_por_cobrar import CuentaPorCobrarViewSet
from finanzas.views.cuentas_por_pagar import CuentaPorPagarViewSet
from finanzas.views.pagos import PagoViewSet
from finanzas.views.reportes import (
    CuentasPorCobrarVencidasView,
    FlujoDeCajaView,
    AnalisisPorClienteProveedorView,
    CuentasPorCobrarAvanzadasView,
    FlujoDeCajaProyectadoView,
    RentabilidadClienteProveedorView,
    CicloConversionEfectivoView,
    LiquidezCorrienteView,
)

# Configura el router para las vistas generales de los modelos
router = DefaultRouter()
router.register(r'cuentas_por_pagar', CuentaPorPagarViewSet, basename='cuentas_por_pagar')
router.register(r'cuentas_por_cobrar', CuentaPorCobrarViewSet, basename='cuentas_por_cobrar')
router.register(r'pagos', PagoViewSet, basename='pagos')



urlpatterns = [
    path('reports/overdue_accounts_receivable/', CuentasPorCobrarVencidasView.as_view(), name='overdue_accounts_receivable'),
    path('reports/cash_flow/', FlujoDeCajaView.as_view(), name='cash_flow'),
    path('reports/customer_supplier_analysis/', AnalisisPorClienteProveedorView.as_view(), name='customer_supplier_analysis'),
    path('reports/advanced_accounts_receivable/', CuentasPorCobrarAvanzadasView.as_view(), name='advanced_accounts_receivable'),
    path('reports/projected_cash_flow/', FlujoDeCajaProyectadoView.as_view(), name='projected_cash_flow'),
    path('reports/customer_supplier_profitability/', RentabilidadClienteProveedorView.as_view(), name='customer_supplier_profitability'),
    path('reports/cash_conversion_cycle/', CicloConversionEfectivoView.as_view(), name='cash_conversion_cycle'),
    path('reports/current_liquidity/', LiquidezCorrienteView.as_view(), name='current_liquidity'),
]

# Incluir las rutas del router (esto es para las vistas de los modelos)
urlpatterns += router.urls
