from django.contrib import admin
from django.urls import path, include
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

def ping(request):
    return JsonResponse({"status": "ok", "message": "Nova ERP API is running"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/ping/', ping),

    # Rutas globales API core
    path('api/', include('core.api.urls')),

    # Rutas específicas de apps
    path('api/auth/', include('accounts.urls')),
    path('auth/', include('social_django.urls', namespace='social')),

    # Documentación y esquema
    path('api/schema/', SpectacularAPIView.as_view(permission_classes=[AllowAny]), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema', permission_classes=[AllowAny]), name='swagger-ui'),

    # **Importar las rutas de inventario correctamente** 
    path('api/inventory/', include('inventario.urls')),  # Esto es lo que estaba comentado

    # *** Aquí agregas las rutas de ventas ***
    path('api/sales/', include('ventas.urls')),

    path('api/core/', include('core.urls')),

    path('api/purchases/', include('compras.urls')),

    path('api/finanzas/', include('finanzas.urls')),

    path('api/contabilidad/', include('contabilidad.urls')),

    path('api/facturacion/', include('facturacion.urls')),

    path('api/reportes/', include('reportes.urls')),

]

