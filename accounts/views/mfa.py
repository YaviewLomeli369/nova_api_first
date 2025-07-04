import pyotp
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.serializers import EnableMFASerializer, VerifyMFASerializer

class EnableMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EnableMFASerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        method = serializer.validated_data['method']

        if method == "totp":
            secret = pyotp.random_base32()
            otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=request.user.email, issuer_name="Nova ERP")
            # Almacenar 'secret' en el modelo de usuario
            return Response({"secret": secret, "uri": otp_uri})
        # Enviar SMS (requiere integración con Twilio o similar)
        return Response({"msg": "Método SMS no implementado"}, status=status.HTTP_501_NOT_IMPLEMENTED)

class VerifyMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VerifyMFASerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        totp = pyotp.TOTP(request.user.profile.mfa_secret)
        if totp.verify(code):
            return Response({"msg": "MFA verificada"})
        return Response({"error": "Código inválido"}, status=400)
