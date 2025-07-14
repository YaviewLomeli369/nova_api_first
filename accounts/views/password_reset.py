# Django
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

# Django REST Framework
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

# Utilidades
import pyotp

# App local
from accounts.models import Usuario
from accounts.utils.auditoria import registrar_auditoria
from accounts.serializers.auth_serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

# Configuración del sitio (ajusta si usas variable de entorno)
site_url = "fca3faea-e64a-4f83-a448-762fa6e71df4-00-1kkfg9j97gplb.spock.replit.dev"
# Ej: site_url = os.environ.get("SITE_URL")


# 📤 Enviar correo de recuperación
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = Usuario.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            reset_url = f"https://{site_url}/api/auth/password-reset/confirm/?uidb64={uidb64}&token={token}"

            send_mail(
                subject="Recuperación de contraseña - Nova ERP",
                message=f"Haz clic en el siguiente enlace para restablecer tu contraseña:\n\n{reset_url}",
                from_email="no-reply@novaerp.com",
                recipient_list=[email],
                fail_silently=False,
            )

            registrar_auditoria(user, "RESET_SOLICITADO", "Usuario", "Solicitud de recuperación de contraseña")
            return Response({"msg": "Correo enviado para recuperación de contraseña"}, status=status.HTTP_200_OK)

        except Usuario.DoesNotExist:
            # Por seguridad, se devuelve siempre éxito
            return Response({"msg": "Correo enviado para recuperación de contraseña"}, status=status.HTTP_200_OK)


# ✅ Confirmar cambio de contraseña
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = serializer.validated_data['uidb64']
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        code = serializer.validated_data.get('code')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            return Response({"error": "Usuario inválido"}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Token inválido o expirado"}, status=status.HTTP_400_BAD_REQUEST)

        # Si tiene MFA habilitado
        if getattr(user, 'mfa_enabled', False):
            if not code:
                return Response({"error": "Código MFA requerido"}, status=status.HTTP_400_BAD_REQUEST)

            totp = pyotp.TOTP(user.mfa_secret)
            if not totp.verify(code):
                registrar_auditoria(user, "RESET_MFA_FAIL", "Usuario", "Código MFA inválido en recuperación")
                return Response({"error": "Código MFA inválido"}, status=status.HTTP_400_BAD_REQUEST)

        # Restablecer contraseña
        user.set_password(password)
        user.save()
        registrar_auditoria(user, "RESET_PASSWORD", "Usuario", "Contraseña restablecida exitosamente")
        return Response({"msg": "Contraseña cambiada correctamente"}, status=status.HTTP_200_OK)

# # Django
# from django.core.mail import send_mail
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_str

# # Django REST Framework
# from rest_framework import status, serializers
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny

# # App local
# from accounts.models import Usuario
# from accounts.utils.auditoria import registrar_auditoria
# from accounts.serializers.auth_serializers import (
#     PasswordResetRequestSerializer,
#     PasswordResetConfirmSerializer
# )

# import pyotp


# site_url = "fca3faea-e64a-4f83-a448-762fa6e71df4-00-1kkfg9j97gplb.spock.replit.dev"


# # ----------------------------------------
# # 🔐 SERIALIZERS (si ya los tienes en accounts.serializers.auth_serializers, no repitas aquí)
# # ----------------------------------------
# # class PasswordResetRequestSerializer(serializers.Serializer):
# #     email = serializers.EmailField()

# # class PasswordResetConfirmSerializer(serializers.Serializer):
# #     uidb64 = serializers.CharField()
# #     token = serializers.CharField()
# #     password = serializers.CharField(min_length=8)
# #     code = serializers.CharField(required=False)  # Solo si tiene MFA


# # ----------------------------------------
# # 📤 SOLICITUD DE RECUPERACIÓN
# # ----------------------------------------

# class PasswordResetRequestView(APIView):
#     permission_classes = [AllowAny]
#     serializer_class = PasswordResetRequestSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         email = serializer.validated_data['email']

#         try:
#             user = Usuario.objects.get(email=email)
#             token = default_token_generator.make_token(user)
#             uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

#             reset_url = f"https://{site_url}/api/auth/password-reset/confirm/?uidb64={uidb64}&token={token}"
#             send_mail(
#                 subject="Recupera tu contraseña",
#                 message=f"Enlace para resetear: {reset_url}",
#                 from_email="no-reply@erp.com",
#                 recipient_list=[email],
#                 fail_silently=False,
#             )
#             return Response({"msg": "Email enviado"}, status=status.HTTP_200_OK)

#         except Usuario.DoesNotExist:
#             # Para no revelar si el email existe o no, puedes devolver éxito aquí también (mejor seguridad)
#             return Response({"msg": "Email enviado"}, status=status.HTTP_200_OK)
#             # Si quieres indicar que no existe:
#             # return Response({"error": "Email no registrado"}, status=status.HTTP_404_NOT_FOUND)


# # ----------------------------------------
# # ✅ CONFIRMACIÓN DEL CAMBIO DE CONTRASEÑA
# # ----------------------------------------

# class PasswordResetConfirmView(APIView):
#     permission_classes = [AllowAny]
#     serializer_class = PasswordResetConfirmSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         uidb64 = serializer.validated_data['uidb64']
#         token = serializer.validated_data['token']
#         password = serializer.validated_data['password']
#         code = serializer.validated_data.get('code')

#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = Usuario.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
#             return Response({"error": "Usuario inválido"}, status=status.HTTP_400_BAD_REQUEST)

#         if default_token_generator.check_token(user, token):
#             if getattr(user, 'mfa_enabled', False):
#                 if not code:
#                     return Response({"error": "Código MFA requerido"}, status=status.HTTP_400_BAD_REQUEST)
#                 totp = pyotp.TOTP(user.mfa_secret)
#                 if not totp.verify(code):
#                     registrar_auditoria(user, "RESET_MFA_FAIL", "Usuario", "Código MFA inválido")
#                     return Response({"error": "Código MFA inválido"}, status=status.HTTP_400_BAD_REQUEST)

#             user.set_password(password)
#             user.save()
#             registrar_auditoria(user, "RESET_PASSWORD", "Usuario", "Contraseña restablecida con éxito")
#             return Response({"msg": "Contraseña cambiada correctamente"}, status=status.HTTP_200_OK)

#         return Response({"error": "Token inválido o expirado"}, status=status.HTTP_400_BAD_REQUEST)


# # # Django
# # from django.core.mail import send_mail
# # from django.contrib.auth.tokens import default_token_generator
# # from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# # from django.utils.encoding import force_bytes, force_str

# # # Django REST Framework
# # from rest_framework import status
# # from rest_framework.views import APIView
# # from rest_framework.response import Response

# # # App local
# # from accounts.models import Usuario
# # from accounts.utils.auditoria import registrar_auditoria
# # from accounts.serializers.auth_serializers import (
# #     PasswordResetRequestSerializer,
# #     PasswordResetConfirmSerializer
# # )

# # import pyotp

# # from rest_framework import serializers


# # site_url = "fca3faea-e64a-4f83-a448-762fa6e71df4-00-1kkfg9j97gplb.spock.replit.dev"

# # # ----------------------------------------
# # # 🔐 SERIALIZERS
# # # ----------------------------------------

# # class PasswordResetRequestSerializer(serializers.Serializer):
# #     email = serializers.EmailField()

# # class PasswordResetConfirmSerializer(serializers.Serializer):
# #     uidb64 = serializers.CharField()
# #     token = serializers.CharField()
# #     password = serializers.CharField(min_length=8)
# #     code = serializers.CharField(required=False)  # Solo si tiene MFA


# # # ----------------------------------------
# # # 📤 SOLICITUD DE RECUPERACIÓN
# # # ----------------------------------------

# # class PasswordResetRequestView(APIView):
# #     serializer_class = PasswordResetRequestSerializer

# #     def post(self, request):
# #         serializer = self.serializer_class(data=request.data)
# #         serializer.is_valid(raise_exception=True)
# #         email = serializer.validated_data['email']

# #         try:
# #             user = Usuario.objects.get(email=email)
# #             token = default_token_generator.make_token(user)
# #             uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

# #             reset_url = f"https://{site_url}/api/auth/password-reset/confirm/?uidb64={uidb64}&token={token}"
# #             send_mail(
# #                 subject="Recupera tu contraseña",
# #                 message=f"Enlace para resetear: {reset_url}",
# #                 from_email="no-reply@erp.com",
# #                 recipient_list=[email],
# #                 fail_silently=False,
# #             )
# #             return Response({"msg": "Email enviado"}, status=200)

# #         except Usuario.DoesNotExist:
# #             return Response({"error": "Email no registrado"}, status=404)

# # # ----------------------------------------
# # # ✅ CONFIRMACIÓN DEL CAMBIO DE CONTRASEÑA
# # # ----------------------------------------

# # class PasswordResetConfirmView(APIView):
# #     serializer_class = PasswordResetConfirmSerializer

# #     def post(self, request):
# #         serializer = self.serializer_class(data=request.data)
# #         serializer.is_valid(raise_exception=True)

# #         uidb64 = serializer.validated_data['uidb64']
# #         token = serializer.validated_data['token']
# #         password = serializer.validated_data['password']
# #         code = serializer.validated_data.get('code')

# #         try:
# #             uid = force_str(urlsafe_base64_decode(uidb64))
# #             user = Usuario.objects.get(pk=uid)
# #         except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
# #             return Response({"error": "Usuario inválido"}, status=400)

# #         if default_token_generator.check_token(user, token):
# #             if getattr(user, 'mfa_enabled', False):
# #                 if not code:
# #                     return Response({"error": "Código MFA requerido"}, status=400)
# #                 totp = pyotp.TOTP(user.mfa_secret)
# #                 if not totp.verify(code):
# #                     registrar_auditoria(user, "RESET_MFA_FAIL", "Usuario", "Código MFA inválido")
# #                     return Response({"error": "Código MFA inválido"}, status=400)

# #             user.set_password(password)
# #             user.save()
# #             registrar_auditoria(user, "RESET_PASSWORD", "Usuario", "Contraseña restablecida con éxito")
# #             return Response({"msg": "Contraseña cambiada correctamente"})

# #         return Response({"error": "Token inválido o expirado"}, status=400)



# # # ----------------------------------------
# # # ✅ CONFIRMACIÓN DEL CAMBIO DE CONTRASEÑA
# # # ----------------------------------------

# # class PasswordResetConfirmView(APIView):
# #     serializer_class = PasswordResetConfirmSerializer
# #     def post(self, request):
# #         serializer = PasswordResetConfirmSerializer(data=request.data)
# #         serializer.is_valid(raise_exception=True)

# #         uidb64 = serializer.validated_data['uidb64']
# #         token = serializer.validated_data['token']
# #         password = serializer.validated_data['password']
# #         code = serializer.validated_data.get('code')

# #         try:
# #             uid = force_str(urlsafe_base64_decode(uidb64))
# #             user = Usuario.objects.get(pk=uid)
# #         except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
# #             return Response({"error": "Usuario inválido"}, status=400)

# #         if default_token_generator.check_token(user, token):
# #             if user.mfa_enabled:
# #                 if not code:
# #                     return Response({"error": "Código MFA requerido"}, status=400)
# #                 totp = pyotp.TOTP(user.mfa_secret)
# #                 if not totp.verify(code):
# #                     registrar_auditoria(user, "RESET_MFA_FAIL", "Usuario", "Código MFA inválido")
# #                     return Response({"error": "Código MFA inválido"}, status=400)

# #             user.set_password(password)
# #             user.save()
# #             registrar_auditoria(user, "RESET_PASSWORD", "Usuario", "Contraseña restablecida con éxito")
# #             return Response({"msg": "Contraseña cambiada correctamente"})

# #         # 🔴 El token es inválido
# #         return Response({"error": "Token inválido o expirado"}, status=400)


