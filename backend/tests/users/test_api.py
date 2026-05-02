from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthApiTests(APITestCase):
    def test_register_creates_user_and_returns_jwt(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "name": "Taylor",
                "email": "taylor@example.com",
                "password": "supersecret123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertTrue(User.objects.filter(email="taylor@example.com").exists())

    @override_settings(ALLOWED_EMAIL_DOMAINS=["company.dev"])
    def test_register_rejects_unapproved_domain(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "name": "Taylor",
                "email": "taylor@example.com",
                "password": "supersecret123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_login_returns_tokens(self):
        User.objects.create_user(name="Taylor", email="taylor@example.com", password="supersecret123")

        response = self.client.post(
            "/api/auth/login/",
            {"email": "taylor@example.com", "password": "supersecret123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_logout_blacklists_refresh_token(self):
        user = User.objects.create_user(name="Taylor", email="taylor@example.com", password="supersecret123")
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.post(
            "/api/auth/logout/",
            {"refresh": str(refresh)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)