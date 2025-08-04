# reportes/urls.py

from django.urls import path
from reportes.views.ventas import ReporteVentasView, PromedioTicketVentaView, ProductosMasVendidosView
from reportes.views.compras import ReporteComprasProveedorView
from reportes.views.flujo_caja import FlujoCajaReporteView, FlujoCajaProyectadoView
from reportes.views.utilidad_producto import ReporteUtilidadPorProductoView
from reportes.views.stock import ReporteStockActualView
from reportes.views.kpi import RentabilidadProductoClienteView, DiasPromedioPagoProveedoresView
from reportes.views.reportes_compras import  DiasPromedioPagoProveedorView
from reportes.views.categorias import CategoriasMasRentablesView
from reportes.views.margen_bruto import MargenBrutoReporteView
from reportes.views.rotacion_inventario import RotacionInventarioView
from reportes.views.eficiencia_compras import EficienciaComprasView




urlpatterns = [
    path('ventas/total/', ReporteVentasView.as_view(), name='reporte-ventas'),
    path('compras/', ReporteComprasProveedorView.as_view(), name='reporte-ventas'),
    path('flujo-de-caja/', FlujoCajaReporteView.as_view(), name='reporte-ventas'),
    path("utilidad-producto/", ReporteUtilidadPorProductoView.as_view(), name="reporte-utilidad-producto"),
    path('stock-actual/', ReporteStockActualView.as_view(), name='reporte-stock-actual'),
    path('kpi/rentabilidad-producto-cliente/', RentabilidadProductoClienteView.as_view(), name='kpi_rentabilidad_producto_cliente'),
    path('kpi/dias-promedio-pago-proveedores/', DiasPromedioPagoProveedoresView.as_view(), name='dias_promedio_pago_proveedores'),
    path('ventas/promedio-ticket/', PromedioTicketVentaView.as_view(), name='promedio-ticket-venta'),
    path('compras/dias-promedio-pago/', DiasPromedioPagoProveedorView.as_view(), name='dias-promedio-pago'),
    path('ventas/productos-mas-vendidos/', ProductosMasVendidosView.as_view(), name='productos-mas-vendidos'),
    path('categorias-mas-rentables/', CategoriasMasRentablesView.as_view(), name='categorias-mas-rentables'),
    path('flujo-caja-proyectado/', FlujoCajaProyectadoView.as_view(), name='flujo-caja-proyectado'),
    path('margen-bruto/', MargenBrutoReporteView.as_view(), name='reporte-margen-bruto'),
    path('rotacion-inventario/', RotacionInventarioView.as_view(), name='rotacion_inventario'),
    path("eficiencia-compras/", EficienciaComprasView.as_view(), name="eficiencia-compras"),
]
