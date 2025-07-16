from compras.views.proveedor_views import ProveedorViewSet


from rest_framework import routers
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'providers', ProveedorViewSet, basename='proveedor')

urlpatterns = [
    path('', include(router.urls)),
]