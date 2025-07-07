# accounts/tests/test_auth.py

from rest_framework.test import APITestCase
from django.urls import reverse
from accounts.models import Usuario
from rest_framework import status

class AuthTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )

    def test_login(self):
        url = reverse("login")  # Asegúrate de tener 'name="login"' en tu URL
        response = self.client.post(url, {"username": "testuser", "password": "testpass123"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_profile_access(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("profile")  # Asegúrate de tener 'name="profile"'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "testuser")

    def test_register_user(self):
        url = reverse("register")
        data = {
            "username": "newuser",
            "password": "newpass123",
            "email": "newuser@example.com"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Usuario.objects.filter(username="newuser").exists())

def test_login_fail(self):
    url = reverse("login")
    response = self.client.post(url, {"username": "wronguser", "password": "wrongpass"})
    self.assertEqual(response.status_code, 401)