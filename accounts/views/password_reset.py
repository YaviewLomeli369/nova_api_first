# accounts/views/password_reset.py

from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from accounts.models import Usuario
from accounts.utils.auditoria import registrar_auditoria

# ----------------------------------------
# 🔐 SERIALIZERS
# ----------------------------------------

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(min_length=8)
    code = serializers.CharField(required=False)  # Solo si tiene MFA


# ----------------------------------------
# 📤 SOLICITUD DE RECUPERACIÓN
# ----------------------------------------

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = Usuario.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            reset_url = f"https://tusitio.com/reset-password/?uidb64={uidb64}&token={token}"
            send_mail(
                subject="Recupera tu contraseña",
                message=f"Enlace para resetear: {reset_url}",
                from_email="no-reply@erp.com",
                recipient_list=[email],
                fail_silently=False,
            )
            return Response({"msg": "Email enviado"}, status=200)

        except Usuario.DoesNotExist:
            return Response({"error": "Email no registrado"}, status=404)


# ----------------------------------------
# ✅ CONFIRMACIÓN DEL CAMBIO DE CONTRASEÑA
# ----------------------------------------

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = serializer.validated_data['uidb64']
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        code = serializer.validated_data.get('code')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            return Response({"error": "Usuario inválido"}, status=400)

        if default_token_generator.check_token(user, token):
            if user.mfa_enabled:
                if not code:
                    return Response({"error": "Código MFA requerido"}, status=400)
                totp = pyotp.TOTP(user.mfa_secret)
                if not totp.verify(code):
                    registrar_auditoria(user, "RESET_MFA_FAIL", "Usuario", "Código MFA inválido")
                    return Response({"error": "Código MFA inválido"}, status=400)

            user.set_password(password)
            user.save()
            registrar_auditoria(user, "RESET_PASSWORD", "Usuario", "Contraseña restablecida con éxito")
            return Response({"msg": "Contraseña cambiada correctamente"})
        # if not default_token_generator.check_token(user, token):
        #     return Response({"error": "Token inválido o expirado"}, status=400)

        # if user.mfa_enabled:
        #     if not code:
        #         return Response({"error": "Código MFA requerido"}, status=400)

        #     totp = pyotp.TOTP(user.mfa_secret)
        #     if not totp.verify(code):
        #         return Response({"error": "Código MFA inválido"}, status=400)

        # user.set_password(password)
        # user.save()
        # return Response({"msg": "Contraseña cambiada correctamente"})

# class PasswordResetConfirmView(APIView):
#     def post(self, request):
#         serializer = PasswordResetConfirmSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         uidb64 = serializer.validated_data['uidb64']
#         token = serializer.validated_data['token']
#         password = serializer.validated_data['password']

#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = Usuario.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
#             return Response({"error": "Usuario inválido"}, status=400)

#         if default_token_generator.check_token(user, token):
#             user.set_password(password)
#             user.save()
#             return Response({"msg": "Contraseña cambiada correctamente"})
#         else:
#             return Response({"error": "Token inválido o expirado"}, status=400)
