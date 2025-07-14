from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from datetime import timedelta
import pyotp

from accounts.models import Usuario
from accounts.serializers.mfa_serializers import (
    MFAEnableSerializer,
    MFAVerifySerializer,
    MFADisableSerializer
)
from accounts.serializers.user_serializers import UsuarioSerializer
from accounts.utils.auditoria import registrar_auditoria

# 🔐 Roles permitidos (definidos previamente en accounts.constants.Roles)
from accounts.permissions import IsSuperAdmin, IsEmpresaAdmin, IsEmpleado, IsAuditor


def generate_temp_token(user):
    access_token = AccessToken.for_user(user)
    access_token.set_exp(lifetime=timedelta(minutes=5))  # Token válido solo 5 minutos
    return str(access_token)


class MFAEnableView(APIView):
    permission_classes = [IsAuthenticated]  # Se puede reforzar con IsEmpresaAdmin | IsEmpleado
    serializer_class = MFAEnableSerializer

    def post(self, request):
        user = request.user
        if user.mfa_enabled:
            return Response({"detail": "MFA ya está activado."}, status=status.HTTP_400_BAD_REQUEST)

        secret = pyotp.random_base32()
        user.mfa_secret = secret
        user.save()

        otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.username,
            issuer_name="Nova ERP"
        )

        return Response({"otp_uri": otp_uri, "secret": secret})


class MFAVerifyView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MFAVerifySerializer

    def post(self, request):
        user = request.user
        serializer = MFAVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']

        if not user.mfa_secret:
            return Response({"detail": "MFA no está configurado para este usuario."}, status=400)

        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(code):
            user.mfa_enabled = True
            user.save()
            registrar_auditoria(user, "MFA_ACTIVADO", "Usuario", "MFA activado correctamente")
            return Response({"detail": "MFA activado correctamente."})

        registrar_auditoria(user, "MFA_FALLIDO", "Usuario", "Código MFA inválido")
        return Response({"detail": "Código MFA inválido. Intenta de nuevo."}, status=400)


class MFADisableView(APIView):
    permission_classes = [IsAuthenticated]  # Se puede reforzar con IsEmpresaAdmin | IsEmpleado
    serializer_class = MFADisableSerializer

    def post(self, request):
        user = request.user
        serializer = MFADisableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']

        if not user.mfa_enabled:
            return Response({"detail": "MFA no está activado."}, status=400)

        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(code):
            user.mfa_enabled = False
            user.mfa_secret = ""
            user.save()
            registrar_auditoria(user, "MFA_DESACTIVADO", "Usuario", "MFA desactivado")
            return Response({"detail": "MFA desactivado correctamente."})

        return Response({"detail": "Código inválido."}, status=400)


class MFALoginVerifyView(APIView):
    permission_classes = [AllowAny]
    serializer_class = MFAVerifySerializer

    def post(self, request):
        token = request.data.get("temp_token")
        code = request.data.get("code")

        if not token or not code:
            return Response({"detail": "Datos incompletos"}, status=400)

        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = Usuario.objects.get(id=user_id)
        except TokenError as e:
            return Response({"detail": "Token inválido o expirado", "error": str(e)}, status=401)
        except KeyError:
            return Response({"detail": "Token mal formado"}, status=400)
        except Usuario.DoesNotExist:
            return Response({"detail": "Usuario no encontrado"}, status=404)

        if not user.mfa_secret:
            return Response({"detail": "2FA no habilitado para este usuario"}, status=400)

        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(code):
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UsuarioSerializer(user).data
            })

        return Response({"detail": "Código MFA inválido"}, status=400)

# # from rest_framework.permissions import AllowAny
# # # Standard Library
# # from datetime import timedelta
# # import pyotp

# # # Django REST Framework
# # from rest_framework.views import APIView
# # from rest_framework.response import Response
# # from rest_framework.permissions import IsAuthenticated
# # from rest_framework import status
# # from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
# # from rest_framework_simplejwt.exceptions import TokenError

# # # App local
# # from accounts.models import Usuario
# # from accounts.serializers.mfa_serializers import (
# #     MFAEnableSerializer,
# #     MFAVerifySerializer,
# #     MFADisableSerializer
# # )
# # from accounts.serializers.user_serializers import UsuarioSerializer
# # from accounts.utils.auditoria import registrar_auditoria

# # from rest_framework import serializers



# # def generate_temp_token(user):
# #     # Crear un AccessToken para el usuario
# #     access_token = AccessToken.for_user(user)
# #     # Aquí puedes agregar más datos si es necesario
# #     access_token.set_exp(lifetime=timedelta(minutes=5))  # Establecer un tiempo de expiración corto
# #     return str(access_token)

# # class MFAEnableView(APIView):
# #     permission_classes = [IsAuthenticated]
# #     serializer_class = MFAEnableSerializer

# #     def post(self, request):
# #         user = request.user
# #         if user.mfa_enabled:
# #             return Response({"detail": "MFA ya está activado."}, status=status.HTTP_400_BAD_REQUEST)

# #         # Generar nuevo secreto
# #         secret = pyotp.random_base32()
# #         user.mfa_secret = secret
# #         user.save()

# #         # Generar URL para QR (otpauth)
# #         otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
# #             name=user.username, issuer_name="Nova ERP"
# #         )

# #         return Response({
# #             "otp_uri": otp_uri,
# #             "secret": secret,  # opcional mostrar clave manualmente
# #         })

# # class MFAVerifyView(APIView):
# #     permission_classes = [IsAuthenticated]
# #     serializer_class = MFAVerifySerializer
    
# #     def post(self, request):
# #         user = request.user
# #         serializer = MFAVerifySerializer(data=request.data)

# #         # Verificar que los datos del serializer son válidos
# #         serializer.is_valid(raise_exception=True)

# #         # Obtener el código MFA del serializer
# #         code = serializer.validated_data['code']

# #         # Verificar si el usuario tiene configurado MFA
# #         if not user.mfa_secret:
# #             return Response(
# #                 {"detail": "MFA no está configurado para este usuario."}, 
# #                 status=status.HTTP_400_BAD_REQUEST
# #             )

# #         # Generar el objeto TOTP y verificar el código
# #         totp = pyotp.TOTP(user.mfa_secret)
# #         if totp.verify(code):
# #             # Si el código es válido, habilitar MFA para el usuario
# #             user.mfa_enabled = True
# #             user.save()

# #             # Registrar la auditoría para activación exitosa
# #             registrar_auditoria(user, "MFA_ACTIVADO", "Usuario", "MFA activado correctamente")

# #             return Response({"detail": "MFA activado correctamente."})
# #         else:
# #             # Registrar la auditoría para intento fallido
# #             registrar_auditoria(user, "MFA_FALLIDO", "Usuario", "Código MFA inválido")

# #             return Response(
# #                 {"detail": "Código MFA inválido. Por favor, intente nuevamente."}, 
# #                 status=status.HTTP_400_BAD_REQUEST
# #             )



# # class MFADisableView(APIView):
# #     permission_classes = [IsAuthenticated]
# #     serializer_class = MFADisableSerializer

# #     def post(self, request):
# #         user = request.user
# #         serializer = MFADisableSerializer(data=request.data)
# #         serializer.is_valid(raise_exception=True)

# #         code = serializer.validated_data['code']
# #         if not user.mfa_enabled:
# #             return Response({"detail": "MFA no está activado."}, status=status.HTTP_400_BAD_REQUEST)

# #         totp = pyotp.TOTP(user.mfa_secret)
# #         if totp.verify(code):
# #             user.mfa_enabled = False
# #             user.mfa_secret = ""
# #             user.save()
# #             registrar_auditoria(user, "MFA_DESACTIVADO", "Usuario", "MFA desactivado")
# #             return Response({"detail": "MFA desactivado correctamente."})
# #         else:
# #             return Response({"detail": "Código inválido."}, status=status.HTTP_400_BAD_REQUEST)




# # class MFALoginVerifyView(APIView):
# #     permission_classes = [AllowAny]
# #     serializer_class = MFAVerifySerializer

# #     def post(self, request):
# #         token = request.data.get("temp_token")
# #         code = request.data.get("code")

# #         if not token or not code:
# #             return Response({"detail": "Datos incompletos"}, status=400)

# #         try:
# #             access_token = AccessToken(token)
# #             user_id = access_token['user_id']
# #             user = Usuario.objects.get(id=user_id)
# #         except TokenError as e:
# #             return Response({"detail": "Token inválido o expirado", "error": str(e)}, status=401)
# #         except KeyError:
# #             return Response({"detail": "Token mal formado"}, status=400)
# #         except Usuario.DoesNotExist:
# #             return Response({"detail": "Usuario no encontrado"}, status=404)

# #         if not user.mfa_secret:
# #             return Response({"detail": "2FA no habilitado para este usuario"}, status=400)

# #         totp = pyotp.TOTP(user.mfa_secret)
# #         if totp.verify(code):
# #             refresh = RefreshToken.for_user(user)
# #             return Response({
# #                 'access': str(refresh.access_token),
# #                 'refresh': str(refresh),
# #                 'user': UsuarioSerializer(user).data
# #             })

# #         return Response({"detail": "Código MFA inválido"}, status=400)


# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
# from rest_framework_simplejwt.exceptions import TokenError
# from datetime import timedelta
# import pyotp

# from accounts.models import Usuario
# from accounts.serializers.mfa_serializers import MFAEnableSerializer, MFAVerifySerializer, MFADisableSerializer
# from accounts.serializers.user_serializers import UsuarioSerializer
# from accounts.utils.auditoria import registrar_auditoria


# def generate_temp_token(user):
#     access_token = AccessToken.for_user(user)
#     access_token.set_exp(lifetime=timedelta(minutes=5))  # Token válido solo 5 minutos
#     return str(access_token)


# class MFAEnableView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = MFAEnableSerializer

#     def post(self, request):
#         user = request.user
#         if user.mfa_enabled:
#             return Response({"detail": "MFA ya está activado."}, status=status.HTTP_400_BAD_REQUEST)

#         secret = pyotp.random_base32()
#         user.mfa_secret = secret
#         user.save()

#         otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user.username, issuer_name="Nova ERP")

#         return Response({"otp_uri": otp_uri, "secret": secret})


# class MFAVerifyView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = MFAVerifySerializer

#     def post(self, request):
#         user = request.user
#         serializer = MFAVerifySerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         code = serializer.validated_data['code']

#         if not user.mfa_secret:
#             return Response({"detail": "MFA no está configurado para este usuario."}, status=status.HTTP_400_BAD_REQUEST)

#         totp = pyotp.TOTP(user.mfa_secret)
#         if totp.verify(code):
#             user.mfa_enabled = True
#             user.save()
#             registrar_auditoria(user, "MFA_ACTIVADO", "Usuario", "MFA activado correctamente")
#             return Response({"detail": "MFA activado correctamente."})
#         else:
#             registrar_auditoria(user, "MFA_FALLIDO", "Usuario", "Código MFA inválido")
#             return Response({"detail": "Código MFA inválido. Intenta de nuevo."}, status=status.HTTP_400_BAD_REQUEST)


# class MFADisableView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = MFADisableSerializer

#     def post(self, request):
#         user = request.user
#         serializer = MFADisableSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         code = serializer.validated_data['code']

#         if not user.mfa_enabled:
#             return Response({"detail": "MFA no está activado."}, status=status.HTTP_400_BAD_REQUEST)

#         totp = pyotp.TOTP(user.mfa_secret)
#         if totp.verify(code):
#             user.mfa_enabled = False
#             user.mfa_secret = ""
#             user.save()
#             registrar_auditoria(user, "MFA_DESACTIVADO", "Usuario", "MFA desactivado")
#             return Response({"detail": "MFA desactivado correctamente."})
#         else:
#             return Response({"detail": "Código inválido."}, status=status.HTTP_400_BAD_REQUEST)


# class MFALoginVerifyView(APIView):
#     permission_classes = [AllowAny]
#     serializer_class = MFAVerifySerializer

#     def post(self, request):
#         token = request.data.get("temp_token")
#         code = request.data.get("code")

#         if not token or not code:
#             return Response({"detail": "Datos incompletos"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             access_token = AccessToken(token)
#             user_id = access_token['user_id']
#             user = Usuario.objects.get(id=user_id)
#         except TokenError as e:
#             return Response({"detail": "Token inválido o expirado", "error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
#         except KeyError:
#             return Response({"detail": "Token mal formado"}, status=status.HTTP_400_BAD_REQUEST)
#         except Usuario.DoesNotExist:
#             return Response({"detail": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

#         if not user.mfa_secret:
#             return Response({"detail": "2FA no habilitado para este usuario"}, status=status.HTTP_400_BAD_REQUEST)

#         totp = pyotp.TOTP(user.mfa_secret)
#         if totp.verify(code):
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 'access': str(refresh.access_token),
#                 'refresh': str(refresh),
#                 'user': UsuarioSerializer(user).data
#             })

#         return Response({"detail": "Código MFA inválido"}, status=status.HTTP_400_BAD_REQUEST)
