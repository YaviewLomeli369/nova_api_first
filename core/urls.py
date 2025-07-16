# core/urls.py
from rest_framework.routers import DefaultRouter
from core.views import EmpresaViewSet

router = DefaultRouter()
router.register(r'empresas', EmpresaViewSet, basename='empresa')

urlpatterns = router.urls