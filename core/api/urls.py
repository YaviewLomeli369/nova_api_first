from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .auth_viewset import AuthViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
]