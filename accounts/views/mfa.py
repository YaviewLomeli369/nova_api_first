# accounts/views/mfa.py

import pyotp
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from accounts.serializers import MFAEnableSerializer, MFAVerifySerializer, MFADisableSerializer

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
            return Response({"detail": "MFA activado correctamente."})
        else:
            return Response({"detail": "Código inválido."}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"detail": "MFA desactivado correctamente."})
        else:
            return Response({"detail": "Código inválido."}, status=status.HTTP_400_BAD_REQUEST)


# import pyotp
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from accounts.serializers import EnableMFASerializer, VerifyMFASerializer

# class EnableMFAView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = EnableMFASerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         method = serializer.validated_data['method']

#         if method == "totp":
#             secret = pyotp.random_base32()
#             otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=request.user.email, issuer_name="Nova ERP")
#             # Almacenar 'secret' en el modelo de usuario
#             return Response({"secret": secret, "uri": otp_uri})
#         # Enviar SMS (requiere integración con Twilio o similar)
#         return Response({"msg": "Método SMS no implementado"}, status=status.HTTP_501_NOT_IMPLEMENTED)

# class VerifyMFAView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = VerifyMFASerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         code = serializer.validated_data['code']
#         totp = pyotp.TOTP(request.user.profile.mfa_secret)
#         if totp.verify(code):
#             return Response({"msg": "MFA verificada"})
#         return Response({"error": "Código inválido"}, status=400)
