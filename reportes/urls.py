# reportes/urls.py

from django.urls import path
from reportes.views.ventas import ReporteVentasView, PromedioTicketVentaView
from reportes.views.compras import ReporteComprasProveedorView
from reportes.views.flujo_caja import FlujoCajaReporteView
from reportes.views.utilidad_producto import ReporteUtilidadPorProductoView
from reportes.views.stock import ReporteStockActualView
from reportes.views.kpi import RentabilidadProductoClienteView



urlpatterns = [
    path('ventas/total/', ReporteVentasView.as_view(), name='reporte-ventas'),
    path('compras/', ReporteComprasProveedorView.as_view(), name='reporte-ventas'),
    path('flujo-de-caja/', FlujoCajaReporteView.as_view(), name='reporte-ventas'),
    path("utilidad-producto/", ReporteUtilidadPorProductoView.as_view(), name="reporte-utilidad-producto"),
    path('stock-actual/', ReporteStockActualView.as_view(), name='reporte-stock-actual'),
    path('kpi/rentabilidad-producto-cliente/', RentabilidadProductoClienteView.as_view(), name='kpi_rentabilidad_producto_cliente'),
    path('ventas/promedio-ticket/', PromedioTicketVentaView.as_view(), name='promedio-ticket-venta')
]
