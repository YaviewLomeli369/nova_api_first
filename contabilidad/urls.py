from django.urls import path, include
from rest_framework.routers import DefaultRouter
from contabilidad.views.asiento_contable import AsientoContableViewSet

router = DefaultRouter()
router.register(r'entries', AsientoContableViewSet, basename='asiento')

urlpatterns = [
    path('', include(router.urls)),
]