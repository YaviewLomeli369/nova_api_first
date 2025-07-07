from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.serializers import LoginSerializer, UsuarioRegistroSerializer, UsuarioSerializer
from accounts.utils.auditoria import registrar_auditoria


class LoginView(APIView):
    permission_classes = [AllowAny]

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


# from rest_framework.serializers import Serializer
# from rest_framework_simplejwt.views import TokenRefreshView
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, generics
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework_simplejwt.tokens import RefreshToken
# from accounts.serializers import LoginSerializer, UsuarioRegistroSerializer, UsuarioSerializer
# from django.contrib.auth import authenticate
# from accounts.utils.auditoria import registrar_auditoria



# from rest_framework.views import APIView
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from rest_framework.exceptions import ValidationError
# from rest_framework_simplejwt.tokens import RefreshToken

# from accounts.serializers import LoginSerializer, UsuarioSerializer
# # from accounts.utils import registrar_auditoria  # Asegúrate de importar correctamente

# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         print("Headers recibidos:", request.headers)
#         serializer = LoginSerializer(data=request.data)
#         try:
#             serializer.is_valid(raise_exception=True)
#         except Exception:
#             username = request.data.get("username", "desconocido")
#             registrar_auditoria(
#                 usuario=None,
#                 username_intentado=username,  # ← Aquí se registra el intento fallido correctamente
#                 accion="LOGIN_FAIL",
#                 tabla="Usuario",
#                 registro=f"Intento fallido de login para '{username}'"
#             )
#             raise

#         user = serializer.validated_data['user']

#         if user.mfa_enabled:
#             temp_token = RefreshToken.for_user(user)
#             registrar_auditoria(
#                 usuario=user,
#                 accion="LOGIN_MFA",
#                 tabla="Usuario",
#                 registro="Login exitoso (pendiente MFA)"
#             )
#             return Response({
#                 'mfa_required': True,
#                 'temp_token': str(temp_token.access_token),
#                 'detail': 'MFA_REQUIRED'
#             }, status=202)

#         refresh = RefreshToken.for_user(user)
#         registrar_auditoria(
#             usuario=user,
#             accion="LOGIN",
#             tabla="Usuario",
#             registro="Login exitoso"
#         )
#         return Response({
#             'access': str(refresh.access_token),
#             'refresh': str(refresh),
#             'user': UsuarioSerializer(user).data
#         })


# # Logout y revocación
# class LogoutView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         try:
#             token = RefreshToken(request.data['refresh'])
#             token.blacklist()
#             registrar_auditoria(
#                 usuario=request.user,
#                 accion="LOGOUT",
#                 tabla="Usuario",
#                 registro="Logout exitoso"
#             )
#             return Response(status=status.HTTP_205_RESET_CONTENT)
#         except Exception:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


# # Registro de usuario
# class RegisterView(generics.CreateAPIView):
#     serializer_class = UsuarioRegistroSerializer
#     permission_classes = [AllowAny]

# # Refresh token (usamos TokenRefreshView de DRF SimpleJWT)
# class RefreshTokenView(TokenRefreshView):
#     permission_classes = [AllowAny]
