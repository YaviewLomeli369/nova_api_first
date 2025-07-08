from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.serializers import LoginSerializer, UsuarioRegistroSerializer, UsuarioSerializer
from accounts.utils.auditoria import registrar_auditoria
from rest_framework.decorators import action, permission_classes

from rest_framework.authentication import BaseAuthentication

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import serializers

class EmptySerializer(serializers.Serializer):
    pass


class NoAuthentication(BaseAuthentication):
    def authenticate(self, request):
        return None



class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    authentication_classes = [NoAuthentication]  # 👈 Esto anula la validación del token
    def post(self, request):
        print("Headers recibidos:", request.headers)
        serializer = LoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            username = request.data.get("username", "desconocido")
            registrar_auditoria(
                usuario=None,
                username_intentado=username,
                accion="LOGIN_FAIL",
                tabla="Usuario",
                registro=f"Intento fallido de login para '{username}'"
            )
            raise

        user = serializer.validated_data['user']

        if getattr(user, 'mfa_enabled', False):
            temp_token = RefreshToken.for_user(user)
            registrar_auditoria(
                usuario=user,
                accion="LOGIN_MFA",
                tabla="Usuario",
                registro="Login exitoso (pendiente MFA)"
            )
            return Response({
                'mfa_required': True,
                'temp_token': str(temp_token.access_token),
                'detail': 'MFA_REQUIRED'
            }, status=202)

        refresh = RefreshToken.for_user(user)
        registrar_auditoria(
            usuario=user,
            accion="LOGIN",
            tabla="Usuario",
            registro="Login exitoso"
        )
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UsuarioSerializer(user).data
        })
        


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"detail": "Refresh token required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            registrar_auditoria(
                usuario=request.user,
                accion="LOGOUT",
                tabla="Usuario",
                registro="Logout exitoso"
            )
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            # Podés agregar logging aquí con e para debug
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    serializer_class = UsuarioRegistroSerializer
    permission_classes = [AllowAny]


class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]


