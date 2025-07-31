# reportes/urls.py

from django.urls import path
from reportes.views.ventas import ReporteVentasView
from reportes.views.compras import ReporteComprasProveedorView
from reportes.views.flujo_caja import FlujoCajaReporteView
from reportes.views.utilidad_producto import ReporteUtilidadPorProductoView

urlpatterns = [
    path('ventas/', ReporteVentasView.as_view(), name='reporte-ventas'),
    path('compras/', ReporteComprasProveedorView.as_view(), name='reporte-ventas'),
    path('flujo-de-caja/', FlujoCajaReporteView.as_view(), name='reporte-ventas'),
    path("utilidad-producto/", ReporteUtilidadPorProductoView.as_view(), name="reporte-utilidad-producto"),
]
