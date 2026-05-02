"""Testes dos endpoints de entrada e presença (Sprint 7)."""
import uuid
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.retrospectives.models import AccessLog, AccessLogAction, Participant, Retrospective, RetrospectiveStatus

User = get_user_model()


def _make_retro(facilitator, *, status_=RetrospectiveStatus.BOARD):
    retro = Retrospective.objects.create(
        title="Sprint Retro",
        team_key="team-alpha",
        facilitator=facilitator,
        status=status_,
        invite_token=uuid.uuid4(),
    )
    Participant.objects.create(retrospective=retro, user=facilitator, votes_remaining=3)
    return retro


class ReopenEntryViewTests(APITestCase):
    def setUp(self):
        self.facilitator = User.objects.create_user(
            name="Facilitator",
            email="fac@example.com",
            password="secret123",
        )
        self.participant = User.objects.create_user(
            name="Participant",
            email="par@example.com",
            password="secret123",
        )
        self.retro = _make_retro(self.facilitator)
        self.url = f"/api/retrospectives/{self.retro.id}/reopen-entry/"

    def test_facilitator_can_reopen_entry(self):
        self.client.force_authenticate(self.facilitator)
        with patch("tasks.invite.auto_block_invite.apply_async"):
            response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "temporarily_open")
        self.assertIn("expires_at", response.data)

        self.retro.refresh_from_db()
        self.assertIsNotNone(self.retro.invite_temporarily_open_until)

        log = AccessLog.objects.filter(
            retrospective=self.retro, action=AccessLogAction.LINK_REOPENED
        ).first()
        self.assertIsNotNone(log)

    def test_non_facilitator_cannot_reopen_entry(self):
        Participant.objects.create(retrospective=self.retro, user=self.participant, votes_remaining=3)
        self.client.force_authenticate(self.participant)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_reopen_during_lobby(self):
        self.retro.status = RetrospectiveStatus.LOBBY
        self.retro.save(update_fields=["status"])
        self.client.force_authenticate(self.facilitator)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_reopen_closed_retro(self):
        self.retro.status = RetrospectiveStatus.CLOSED
        self.retro.save(update_fields=["status"])
        self.client.force_authenticate(self.facilitator)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class InviteStatusViewTests(APITestCase):
    def setUp(self):
        self.facilitator = User.objects.create_user(
            name="Facilitator",
            email="fac2@example.com",
            password="secret123",
        )
        self.retro = _make_retro(self.facilitator)
        self.url = f"/api/retrospectives/{self.retro.id}/invite-status/"
        self.client.force_authenticate(self.facilitator)

    def test_active_during_lobby(self):
        self.retro.status = RetrospectiveStatus.LOBBY
        self.retro.save(update_fields=["status"])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "active")

    def test_temporarily_open_when_window_active(self):
        self.retro.invite_temporarily_open_until = timezone.now() + timedelta(minutes=2)
        self.retro.save(update_fields=["invite_temporarily_open_until"])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "temporarily_open")
        self.assertIsNotNone(response.data["expires_at"])

    def test_blocked_when_window_expired(self):
        self.retro.invite_temporarily_open_until = timezone.now() - timedelta(seconds=1)
        self.retro.save(update_fields=["invite_temporarily_open_until"])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "blocked")

    def test_blocked_when_no_window_set(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "blocked")


class PresenceViewTests(APITestCase):
    def setUp(self):
        self.facilitator = User.objects.create_user(
            name="Facilitator",
            email="fac3@example.com",
            password="secret123",
        )
        self.retro = _make_retro(self.facilitator)
        self.url = f"/api/retrospectives/{self.retro.id}/presence/"
        self.client.force_authenticate(self.facilitator)

    def test_returns_participants_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("participants", response.data)
        self.assertEqual(len(response.data["participants"]), 1)
        participant = response.data["participants"][0]
        self.assertEqual(participant["name"], "Facilitator")
        self.assertIn("joined_at", participant)

    def test_returns_all_participants(self):
        p2 = User.objects.create_user(name="User2", email="u2@example.com", password="secret123")
        Participant.objects.create(retrospective=self.retro, user=p2, votes_remaining=3)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data["participants"]), 2)
