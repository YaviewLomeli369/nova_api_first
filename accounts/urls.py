from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import auth, profile, password_reset, mfa, audit, users
from accounts.views.roles import RolViewSet
from accounts.views.users import UsuarioViewSet

router = DefaultRouter()
router.register(r'users', users.UsuarioViewSet, basename='usuarios')
router.register(r'roles', roles.RolViewSet)

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
    path('audit-log/', audit.AuditLogView.as_view()),
    path('', include(router.urls)),
]


# from django.urls import path
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
#     TokenVerifyView,
# )

# urlpatterns = [
#     path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
# ]
