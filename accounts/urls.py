# accounts/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importación de vistas por módulos
from accounts.views import auth, profile, password_reset, mfa, audit, users
from accounts.views.roles import RolViewSet
from accounts.views.users import UsuarioViewSet
from accounts.views.audit import AuditLogListView, AuditLogExportCSV
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views.mfa import MFAEnableView, MFAVerifyView, MFADisableView, MFALoginVerifyView

# Rutas registradas con router para vistas basadas en ViewSet
router = DefaultRouter()
router.register(r'users', UsuarioViewSet, basename='usuarios')
router.register(r'roles', RolViewSet)

# Lista de URLs explícitas
urlpatterns = [

    # --- Autenticación ---
    path('login/', auth.LoginView.as_view(), name='login'),                        # POST - Iniciar sesión
    path('logout/', auth.LogoutView.as_view(), name='logout'),                     # POST - Cerrar sesión
    path('register/', auth.RegisterView.as_view(), name='register'),               # POST - Registro de usuario
    path('refresh/', auth.RefreshTokenView.as_view(), name='token-refresh'),       # POST - Refrescar token JWT

    # --- Perfil de usuario ---
    path('profile/', profile.ProfileView.as_view(), name='profile'),               # GET/PUT - Ver o editar perfil

    # --- Recuperación de contraseña ---
    path('password-reset/request/', password_reset.PasswordResetRequestView.as_view(), name='password-reset-request'),  # POST - Solicitar reinicio
    path('password-reset/confirm/', password_reset.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    # path('password-reset/confirm/', password_reset.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),  # POST - Confirmar reinicio

    # --- Autenticación de dos factores (2FA) ---
    path('2fa/verify-login/', MFALoginVerifyView.as_view(), name='mfa-verify-login'),  # POST - Verificar 2FA en login
    path('2fa/enable/', MFAEnableView.as_view(), name='mfa-enable'),                   # POST - Habilitar 2FA
    path('2fa/verify/', MFAVerifyView.as_view(), name='mfa-verify'),                   # POST - Verificar código 2FA
    path('2fa/disable/', MFADisableView.as_view(), name='mfa-disable'),                # POST - Deshabilitar 2FA

    # --- Actividad del usuario ---
    path('activity/', audit.ActivityLogView.as_view(), name='activity-log'),                # GET - Ver actividad

    # --- Auditoría ---
    path('audit-log/', AuditLogListView.as_view(), name='audit-log-list'),                  # GET - Lista de logs de auditoría
    path('audit-log/export-csv/', AuditLogExportCSV.as_view(), name='audit-log-export-csv'),# GET - Exportar logs como CSV

    # --- Vistas registradas mediante router (ViewSets) ---
    path('', include(router.urls)),

]

