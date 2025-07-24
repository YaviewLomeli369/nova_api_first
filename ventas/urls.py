# ventas/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path
from ventas.views import ClienteViewSet, VentaViewSet, DetalleVentaViewSet
from ventas.views.dashboard import VentaDashboardAPIView  # Asegúrate de importar desde el archivo correcto
from ventas.views.facturar_venta import FacturarVentaAPIView  # Asegúrate que esta vista existe y está bien importada
# Instanciamos el router
router = DefaultRouter()
router.register(r'costumers', ClienteViewSet)
router.register(r'orders', VentaViewSet)
router.register(r'details', DetalleVentaViewSet)

# Añadimos el endpoint del dashboard de ventas fuera del router
urlpatterns = router.urls + [
    path('dashboard/', VentaDashboardAPIView.as_view(), name='venta-dashboard'),
    path('invoice-sale/<int:id>/', FacturarVentaAPIView.as_view(), name='facturar-venta'),
]

