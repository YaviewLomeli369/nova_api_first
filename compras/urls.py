from compras.views.proveedor_views import ProveedorViewSet


from rest_framework import routers
from django.urls import path, include
from compras.views.compra_views import CompraViewSet

router = routers.DefaultRouter()
router.register(r'providers', ProveedorViewSet, basename='proveedor')
router.register(r'purchases', CompraViewSet, basename='purchases')

urlpatterns = [
    path('', include(router.urls)),
]