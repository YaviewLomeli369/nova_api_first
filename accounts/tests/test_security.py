from rest_framework.test import APITestCase
from django.urls import reverse
from accounts.models import Usuario
from rest_framework_simplejwt.tokens import RefreshToken
import pyotp

class SeguridadTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username="testuser", password="Test1234", email="test@example.com"
        )

    def test_login_fail_auditoria(self):
        url = reverse("login")
        response = self.client.post(url, {"username": "wrong", "password": "bad"})
        self.assertEqual(response.status_code, 401)

    def test_login_con_mfa(self):
        self.user.mfa_enabled = True
        self.user.mfa_secret = pyotp.random_base32()
        self.user.save()

        url = reverse("login")
        response = self.client.post(url, {"username": "testuser", "password": "Test1234"})
        self.assertEqual(response.status_code, 202)
        self.assertIn("temp_token", response.data)

        # MFA TOTP correcto
        totp = pyotp.TOTP(self.user.mfa_secret)
        code = totp.now()
        verify_url = reverse("mfa-verify-login")
        response = self.client.post(verify_url, {"temp_token": response.data["temp_token"], "code": code})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

# CORS correctamente configurado:
# Solo responde a dominios permitidos:


# // En frontend en local
# fetch('https://api.tusitio.com/api/login')
# → debe fallar si el dominio no está en CORS_ALLOWED_ORIGINS
# Rate Limiting activado:
# Lanza 10 peticiones rápidas y ve si responde:


# {
#   "detail": "Request was throttled. Expected available in X seconds."
# }