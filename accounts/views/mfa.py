# accounts/views/mfa.py

import pyotp
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from accounts.serializers import MFAEnableSerializer, MFAVerifySerializer, MFADisableSerializer
from rest_framework.permissions import AllowAny
from accounts.utils.auditoria import registrar_auditoria

class MFAEnableView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.mfa_enabled:
            return Response({"detail": "MFA ya está activado."}, status=status.HTTP_400_BAD_REQUEST)

        # Generar nuevo secreto
        secret = pyotp.random_base32()
        user.mfa_secret = secret
        user.save()

        # Generar URL para QR (otpauth)
        otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.username, issuer_name="Nova ERP"
        )

        return Response({
            "otp_uri": otp_uri,
            "secret": secret,  # opcional mostrar clave manualmente
        })

class MFAVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = MFAVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']
        if not user.mfa_secret:
            return Response({"detail": "MFA no está configurado."}, status=status.HTTP_400_BAD_REQUEST)

        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(code):
            user.mfa_enabled = True
            user.save()
            registrar_auditoria(user, "MFA_ACTIVADO", "Usuario", "MFA activado correctamente")
            return Response({"detail": "MFA activado correctamente."})
        else:
            registrar_auditoria(user, "MFA_FALLIDO", "Usuario", "Código MFA inválido")
            return Response({"detail": "Código inválido."}, status=400)
        # if totp.verify(code):
        #     user.mfa_enabled = True
        #     user.save()
        #     return Response({"detail": "MFA activado correctamente."})
        # else:
        #     return Response({"detail": "Código inválido."}, status=status.HTTP_400_BAD_REQUEST)

class MFADisableView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = MFADisableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']
        if not user.mfa_enabled:
            return Response({"detail": "MFA no está activado."}, status=status.HTTP_400_BAD_REQUEST)

        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(code):
            user.mfa_enabled = False
            user.mfa_secret = ""
            user.save()
            registrar_auditoria(user, "MFA_DESACTIVADO", "Usuario", "MFA desactivado")
            return Response({"detail": "MFA desactivado correctamente."})
        else:
            return Response({"detail": "Código inválido."}, status=status.HTTP_400_BAD_REQUEST)

class MFALoginVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("temp_token")
        code = request.data.get("code")

        if not token or not code:
            return Response({"detail": "Datos incompletos"}, status=400)

        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = Usuario.objects.get(id=user_id)
        except:
            return Response({"detail": "Token inválido"}, status=400)

        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(code):
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UsuarioSerializer(user).data
            })
        return Response({"detail": "Código MFA inválido"}, status=400)