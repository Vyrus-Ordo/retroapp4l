from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.retrospectives.models import Participant, Retrospective, RetrospectiveStatus

User = get_user_model()


class RetrospectiveApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(name="Facilitator", email="facilitator@example.com", password="supersecret123")
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
            Participant.objects.filter(retrospective=retrospective, user=self.user, votes_remaining=retrospective.max_votes_per_user).exists()
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