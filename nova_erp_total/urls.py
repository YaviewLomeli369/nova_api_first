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
]


# """
# nova_erp_total URL Configuration
# URL configuration for nova_erp_total project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.0/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# from django.contrib import admin
# from django.urls import path
# from django.urls.conf import include
# from rest_framework.permissions import AllowAny
# #JSON RESPONSE
# from django.http import JsonResponse

# #SPECTACULAR
# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# #PRUEBA JSON RESOPNSE
# def ping(request):
#     return JsonResponse({"status": "ok", "message": "Nova ERP API is running"})



# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/ping/', ping),

#     # Aquí montas los JWT
#     path('api/auth/', include('accounts.urls')),

#     path('auth/', include('social_django.urls', namespace='social')),

#     # 
#     path('api/schema/', SpectacularAPIView.as_view(permission_classes=[AllowAny]), name='schema'),
#     path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema', permission_classes=[AllowAny]), name='swagger-ui'),
#     # path('api/schema/', SpectacularAPIView.as_view(permission_classes=[AllowAny]), name='schema'),
#     # path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema', permission_classes=[AllowAny]), name='swagger-ui'),
#     # otras rutas...
#     # path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
#     # path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui')
# ]
