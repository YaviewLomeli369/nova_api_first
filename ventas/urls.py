from rest_framework.routers import DefaultRouter
from ventas.views import ClienteViewSet, VentaViewSet, DetalleVentaViewSet

router = DefaultRouter()
router.register(r'costumers', ClienteViewSet)
router.register(r'orders', VentaViewSet)
router.register(r'details', DetalleVentaViewSet)

urlpatterns = router.urls
