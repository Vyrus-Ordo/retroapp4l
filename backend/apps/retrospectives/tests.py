from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.retrospectives.models import Participant, Retrospective, RetrospectiveStatus

User = get_user_model()


class RetrospectiveApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			name="Facilitator",
			email="facilitator@example.com",
			password="supersecret123",
		)
		self.client.force_authenticate(self.user)

	def test_create_retrospective_starts_in_setup_and_adds_participant(self):
		response = self.client.post(
			"/api/retrospectives/",
			{
				"title": "Sprint 1 Retro",
				"sprint_name": "Sprint 1",
				"team_key": "platform-team",
				"description": "Looking back on foundation work.",
			},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		retrospective = Retrospective.objects.get(id=response.data["id"])
		self.assertEqual(retrospective.status, RetrospectiveStatus.SETUP)
		self.assertTrue(
			Participant.objects.filter(
				retrospective=retrospective,
				user=self.user,
				votes_remaining=retrospective.max_votes_per_user,
			).exists()
		)

	def test_list_returns_retrospectives_for_facilitator_and_participant(self):
		owned = Retrospective.objects.create(title="Owned", team_key="alpha", facilitator=self.user)
		other_user = User.objects.create_user(name="Guest", email="guest@example.com", password="supersecret123")
		joined = Retrospective.objects.create(title="Joined", team_key="beta", facilitator=other_user)
		Participant.objects.create(retrospective=joined, user=self.user, votes_remaining=3)

		response = self.client.get("/api/retrospectives/")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		returned_ids = {item["id"] for item in response.data}
		self.assertEqual(returned_ids, {str(owned.id), str(joined.id)})

	def test_team_suggestions_returns_distinct_keys_for_facilitator(self):
		Retrospective.objects.create(title="One", team_key="alpha", facilitator=self.user)
		Retrospective.objects.create(title="Two", team_key="alpha", facilitator=self.user)
		Retrospective.objects.create(title="Three", team_key="beta", facilitator=self.user)

		response = self.client.get("/api/teams/suggestions/")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["suggestions"], ["alpha", "beta"])

	def test_invite_resolve_exposes_public_metadata(self):
		retrospective = Retrospective.objects.create(
			title="Sprint 7 Retro",
			team_key="platform",
			facilitator=self.user,
			status=RetrospectiveStatus.LOBBY,
			invite_token="5eb3f5a5-ffce-45a4-a4e1-e746263605e8",
		)

		response = self.client.get(f"/api/invites/{retrospective.invite_token}/")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["id"], str(retrospective.id))
		self.assertEqual(response.data["invite_status"], "active")

	def test_invite_join_creates_guest_user_and_participant(self):
		retrospective = Retrospective.objects.create(
			title="Sprint 8 Retro",
			team_key="platform",
			facilitator=self.user,
			status=RetrospectiveStatus.LOBBY,
			invite_token="2f4c6f8c-5518-4526-b4d3-83e8bc57c3eb",
		)

		self.client.force_authenticate(user=None)
		response = self.client.post(
			f"/api/invites/{retrospective.invite_token}/join/",
			{"name": "Convidada", "email": "convidada@example.com"},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		guest = User.objects.get(id=response.data["user"]["id"])
		self.assertTrue(guest.is_guest)
		self.assertEqual(guest.public_email, "convidada@example.com")
		self.assertTrue(
			Participant.objects.filter(retrospective=retrospective, user=guest).exists()
		)

	def test_invite_join_reuses_authenticated_guest_identity(self):
		retrospective = Retrospective.objects.create(
			title="Sprint 9 Retro",
			team_key="platform",
			facilitator=self.user,
			status=RetrospectiveStatus.LOBBY,
			invite_token="64bd4b74-2cc7-431b-91d7-6da9ccb3b0b8",
		)
		guest = User.objects.create_user(
			name="Visitante Antigo",
			email="guest+existing@guest.retroapp4l.local",
			public_email="old@example.com",
			is_guest=True,
		)
		guest.set_unusable_password()
		guest.save(update_fields=["password"])
		refresh = RefreshToken.for_user(guest)
		self.client.force_authenticate(user=None)
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

		response = self.client.post(
			f"/api/invites/{retrospective.invite_token}/join/",
			{"name": "Visitante Novo", "email": "novo@example.com"},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		guest.refresh_from_db()
		self.assertEqual(guest.name, "Visitante Novo")
		self.assertEqual(guest.public_email, "novo@example.com")
		self.assertTrue(
			Participant.objects.filter(retrospective=retrospective, user=guest).exists()
		)

# Create your tests here.
