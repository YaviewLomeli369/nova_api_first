from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from accounts.models import Usuario

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = Usuario.objects.get(email=email)
            token = default_token_generator.make_token(user)
            reset_url = f"https://tusitio.com/reset-password/?token={token}"
            send_mail("Recupera tu contraseña", f"Enlace: {reset_url}", "no-reply@erp.com", [email])
            return Response({"msg": "Email enviado"}, status=200)
        except Usuario.DoesNotExist:
            return Response({"error": "Email no registrado"}, status=404)

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        # Aquí se puede verificar el token con algún sistema de validación (no implementado completo)
        return Response({"msg": "Contraseña cambiada correctamente"})
