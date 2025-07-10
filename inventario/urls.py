from rest_framework.routers import DefaultRouter
from django.urls import path
from inventario.views.producto import ProductoViewSet
from inventario.views.categoria import CategoriaViewSet  # Asumido: Vista para categorías
from inventario.views.inventario import InventarioViewSet
from inventario.views.movimiento import MovimientoInventarioViewSet
from inventario.views.stock_alerts import StockAlertView
from inventario.views.batches import BatchView

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
]


# from rest_framework.routers import DefaultRouter
# from django.urls import path
# from inventario.views.producto import ProductoViewSet
# from inventario.views.inventario import InventarioViewSet
# from inventario.views.movimiento import MovimientoInventarioViewSet
# from inventario.views.stock_alerts import StockAlertView
# from inventario.views.batches import BatchView

# # Crear un enrutador para el registro de vistas (ViewSets)
# router = DefaultRouter()
# router.register(r'products', ProductoViewSet, basename='product')
# router.register(r'inventory', InventarioViewSet, basename='inventory')
# router.register(r'movements', MovimientoInventarioViewSet, basename='inventory-movement')


# # Lista de URLs que combinan las rutas generadas por el router con otras rutas personalizadas
# urlpatterns = router.urls + [
#     # Rutas personalizadas adicionales
#     path('inventory/stock-alerts/', StockAlertView.as_view(), name='stock-alerts'),
#     path('inventory/batches/', BatchView.as_view(), name='inventory-batches'),
# ]
# # from rest_framework.routers import DefaultRouter
# # from django.urls import path
# # from inventario.views.producto import ProductoViewSet
# # from inventario.views.inventario import InventarioViewSet
# # from inventario.views.movimiento import MovimientoInventarioViewSet
# # from inventario.views.stock_alerts import StockAlertView
# # from inventario.views.batches import BatchView

# # # Crear un enrutador para el registro de vistas (ViewSets)
# # router = DefaultRouter()
# # router.register(r'products', ProductoViewSet, basename='product')
# # router.register(r'inventory', InventarioViewSet, basename='inventory')
# # router.register(r'inventory/movements', MovimientoInventarioViewSet, basename='inventory-movement')


# # # Lista de URLs que combinan las rutas generadas por el router con otras rutas personalizadas
# # urlpatterns = router.urls + [
# #     # Rutas personalizadas adicionales
# #     path('inventory/stock-alerts/', StockAlertView.as_view(), name='stock-alerts'),
# #     path('inventory/batches/', BatchView.as_view(), name='inventory-batches'),
# # ]
# # # inventario/urls.py

# # from rest_framework.routers import DefaultRouter
# # from django.urls import path
# # from inventario.views.producto import ProductoViewSet
# # from inventario.views.inventario import InventarioViewSet
# # from inventario.views.movimiento import MovimientoInventarioViewSet
# # from inventario.views.stock_alerts import StockAlertView
# # from inventario.views.batches import BatchView

# # router = DefaultRouter()
# # router.register(r'products', ProductoViewSet, basename='product')
# # router.register(r'inventory', InventarioViewSet, basename='inventory')
# # router.register(r'inventory/movements', MovimientoInventarioViewSet, basename='inventory-movement')

# # urlpatterns = router.urls + [
# #     path('inventory/stock-alerts/', StockAlertView.as_view(), name='stock-alerts'),
# #     path('inventory/batches/', BatchView.as_view(), name='inventory-batches'),
# # ]


# # inventario

# # 🔹 4. /movimientos/ → MovimientoInventarioViewSet
# # Método	Ruta	Acción
# # GET	/api/inventario/movimientos/	Listar movimientos
# # POST	/api/inventario/movimientos/	Crear nuevo movimiento
# # GET	/api/inventario/movimientos/{id}/	Ver detalle de movimiento
# # PUT	/api/inventario/movimientos/{id}/	❌ No recomendado (stock ya movido)
# # PATCH	/api/inventario/movimientos/{id}/	❌ Idem anterior
# # DELETE	/api/inventario/movimientos/{id}/	❌ No recomendado (auditoría)

# # # inventario/urls.py

# # from rest_framework.routers import DefaultRouter
# # from django.urls import path, include

# # from inventario.views.categoria import CategoriaViewSet
# # from inventario.views.producto import ProductoViewSet
# # from inventario.views.inventario import InventarioViewSet
# # from inventario.views.movimiento import MovimientoInventarioViewSet

# # router = DefaultRouter()
# # router.register(r'categorias', CategoriaViewSet, basename='categoria')
# # router.register(r'productos', ProductoViewSet, basename='producto')
# # router.register(r'inventarios', InventarioViewSet, basename='inventario')
# # router.register(r'movimientos', MovimientoInventarioViewSet, basename='movimiento-inventario')

# # urlpatterns = [
# #     path('', include(router.urls)),
# # ]
