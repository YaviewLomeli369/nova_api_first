# 🛡️ Django REST Framework
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.authentication import BaseAuthentication, BasicAuthentication

# 🔑 JWT
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError

# 🧾 Serializers
from accounts.serializers.auth_serializers import LoginSerializer
from accounts.serializers.user_serializers import UsuarioRegistroSerializer, UsuarioSerializer

# 🧠 Auditoría
from accounts.utils.auditoria import registrar_auditoria


# 🔹 Serializer vacío para endpoints sin entrada
class EmptySerializer(serializers.Serializer):
    pass


# 🔹 Desactiva autenticación para ciertos endpoints como login
class NoAuthentication(BaseAuthentication):
    def authenticate(self, request):
        return None


# ✅ LOGIN CON AUDITORÍA Y SOPORTE PARA MFA
class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = [NoAuthentication]  # ignora token JWT aquí

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

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


# ✅ LOGOUT CON BLACKLIST Y AUDITORÍA
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {"detail": "Se requiere el refresh token para cerrar sesión."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            registrar_auditoria(
                usuario=request.user,
                accion="LOGOUT",
                tabla="Usuario",
                registro="Logout exitoso"
            )

            return Response(
                {"detail": "Sesión cerrada correctamente."},
                status=status.HTTP_205_RESET_CONTENT
            )

        except TokenError:
            return Response(
                {"detail": "El token ya fue usado o es inválido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            return Response(
                {"detail": "Error inesperado al cerrar sesión."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ✅ REGISTRO DE USUARIOS (público o controlable por rol)
class RegisterView(generics.CreateAPIView):
    serializer_class = UsuarioRegistroSerializer
    permission_classes = [AllowAny]
    authentication_classes = [BasicAuthentication]  # útil para apps móviles o sistemas externos


# ✅ REFRESCAR TOKEN JWT
class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]



# # Django REST Framework
# from rest_framework.views import APIView
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status, generics
# from rest_framework.exceptions import ValidationError
# from rest_framework.authentication import BaseAuthentication
# from rest_framework.generics import GenericAPIView

# # JWT
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.views import TokenRefreshView
# from rest_framework_simplejwt.exceptions import TokenError

# # Serializers (ya divididos en archivos separados)
# from accounts.serializers.auth_serializers import LoginSerializer
# from accounts.serializers.user_serializers import UsuarioRegistroSerializer, UsuarioSerializer

# # Utilidades
# from accounts.utils.auditoria import registrar_auditoria
# from rest_framework import serializers
# from rest_framework.authentication import BasicAuthentication


# class EmptySerializer(serializers.Serializer):
#     pass


# class NoAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         return None



# class LoginView(APIView):
#     serializer_class = LoginSerializer
#     permission_classes = [AllowAny]
    
#     authentication_classes = [NoAuthentication]  # 👈 Esto anula la validación del token
#     def post(self, request):
#         print("Headers recibidos:", request.headers)
#         serializer = LoginSerializer(data=request.data)
#         try:
#             serializer.is_valid(raise_exception=True)
#         except ValidationError:
#             username = request.data.get("username", "desconocido")
#             registrar_auditoria(
#                 usuario=None,
#                 username_intentado=username,
#                 accion="LOGIN_FAIL",
#                 tabla="Usuario",
#                 registro=f"Intento fallido de login para '{username}'"
#             )
#             raise

#         user = serializer.validated_data['user']

#         if getattr(user, 'mfa_enabled', False):
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
        
# class LogoutView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = EmptySerializer

#     def post(self, request):
#         refresh_token = request.data.get('refresh')

#         if not refresh_token:
#             return Response(
#                 {"detail": "Se requiere el refresh token para cerrar sesión."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             token = RefreshToken(refresh_token)

#             # Intenta agregarlo a la blacklist
#             token.blacklist()

#             registrar_auditoria(
#                 usuario=request.user,
#                 accion="LOGOUT",
#                 tabla="Usuario",
#                 registro="Logout exitoso"
#             )

#             return Response(
#                 {"detail": "Sesión cerrada correctamente."},
#                 status=status.HTTP_205_RESET_CONTENT
#             )

#         except TokenError as e:
#             # Token ya fue rotado o está en blacklist
#             return Response(
#                 {"detail": "El token ya fue usado o es inválido."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         except Exception as e:
#             # Otros errores inesperados
#             return Response(
#                 {"detail": "Error inesperado al cerrar sesión."},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


# class RegisterView(generics.CreateAPIView):
#     serializer_class = UsuarioRegistroSerializer
#     permission_classes = [AllowAny]
#     authentication_classes = [BasicAuthentication]  # 👈 Esto ignora JWT y permite registro sin token


# class RefreshTokenView(TokenRefreshView):
#     permission_classes = [AllowAny]


