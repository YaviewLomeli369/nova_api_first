# core/urls.py
from rest_framework.routers import DefaultRouter
from core.views import EmpresaViewSet, SucursalViewSet

router = DefaultRouter()
router.register(r'companies', EmpresaViewSet, basename='empresa')
router.register(r'branches', SucursalViewSet, basename='sucursal')


urlpatterns = router.urls