from rest_framework.routers import DefaultRouter
from django.urls import path
from inventario.views.producto import ProductoViewSet
from inventario.views.categoria import CategoriaViewSet  # Asumido: Vista para categorías
from inventario.views.inventario import InventarioViewSet
from inventario.views.movimiento import MovimientoInventarioViewSet
from inventario.views.stock_alerts import StockAlertView
from inventario.views.batches import BatchView
from inventario.views.movimientos_debug import MovimientosRecientesView

# Crear un enrutador para el registro de vistas (ViewSets)
router = DefaultRouter()
router.register(r'products', ProductoViewSet, basename='product')  # Endpoint para productos
router.register(r'categories', CategoriaViewSet, basename='category')  # Endpoint para categorías
router.register(r'inventory', InventarioViewSet, basename='inventory')  # Endpoint para inventario
router.register(r'movements', MovimientoInventarioViewSet, basename='inventory-movement')  # Endpoint para movimientos

# Lista de URLs que combinan las rutas generadas por el router con otras rutas personalizadas
urlpatterns = router.urls + [
    # Rutas personalizadas adicionales (las nuevas que mencionabas)
    path('stock-alerts/', StockAlertView.as_view(), name='stock-alerts'),  # Rutas para las alertas de stock
    path('batches/', BatchView.as_view(), name='inventory-batches'),  # Rutas para lotes de inventario
    path('movimientos-recientes/', MovimientosRecientesView.as_view(), name='movimientos-recientes'),
]