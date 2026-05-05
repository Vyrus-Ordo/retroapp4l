from unittest.mock import patch

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


class TurnstileRegistrationTests(APITestCase):
    """Registration endpoint Turnstile protection."""

    def test_register_bypasses_turnstile_when_secret_key_is_empty(self):
        """Empty CLOUDFLARE_TURNSTILE_SECRET_KEY skips verification (dev/test)."""
        with self.settings(CLOUDFLARE_TURNSTILE_SECRET_KEY=""):
            response = self.client.post(
                "/api/auth/register/",
                {"name": "Bot", "email": "bot@example.com", "password": "supersecret123"},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @override_settings(CLOUDFLARE_TURNSTILE_SECRET_KEY="test-secret")
    @patch("apps.users.views.verify_turnstile", return_value=False)
    def test_register_rejects_invalid_turnstile_token(self, _mock):
        """Returns 400 when Turnstile verification fails."""
        response = self.client.post(
            "/api/auth/register/",
            {
                "name": "Bot",
                "email": "bot2@example.com",
                "password": "supersecret123",
                "cf_turnstile_response": "bad-token",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cf_turnstile_response", response.data)

    @override_settings(CLOUDFLARE_TURNSTILE_SECRET_KEY="test-secret")
    @patch("apps.users.views.verify_turnstile", return_value=True)
    def test_register_succeeds_with_valid_turnstile_token(self, _mock):
        """Returns 201 when Turnstile verification passes."""
        response = self.client.post(
            "/api/auth/register/",
            {
                "name": "Human",
                "email": "human@example.com",
                "password": "supersecret123",
                "cf_turnstile_response": "valid-token",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)