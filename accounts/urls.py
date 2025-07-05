from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import auth, profile, password_reset, mfa, audit, users
from accounts.views.roles import RolViewSet
from accounts.views.users import UsuarioViewSet
from accounts.views.audit import AuditLogListView, AuditLogExportCSV
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = DefaultRouter()
router.register(r'users', users.UsuarioViewSet, basename='usuarios')
router.register(r'roles', RolViewSet)

urlpatterns = [
    path('login/', auth.LoginView.as_view()),
    path('logout/', auth.LogoutView.as_view()),
    path('register/', auth.RegisterView.as_view()),
    path('refresh/', auth.RefreshTokenView.as_view()),
    path('profile/', profile.ProfileView.as_view()),
    path('password-reset/request/', password_reset.PasswordResetRequestView.as_view()),
    path('password-reset/confirm/', password_reset.PasswordResetConfirmView.as_view()),
    path('2fa/enable/', mfa.EnableMFAView.as_view()),
    path('2fa/verify/', mfa.VerifyMFAView.as_view()),
    path('activity/', audit.ActivityLogView.as_view()),
    # path('audit-log/', audit.AuditLogView.as_view()),
    path('audit-log/', AuditLogListView.as_view(), name='audit-log-list'),
    path('audit-log/export-csv/', AuditLogExportCSV.as_view(), name='audit-log-export-csv'),
    path('', include(router.urls)),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]