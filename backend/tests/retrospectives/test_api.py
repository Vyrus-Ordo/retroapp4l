from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.retrospectives.models import Milestone, MilestoneCategory, Participant, Retrospective, RetrospectiveStatus

User = get_user_model()


class RetrospectiveApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(name="Facilitator", email="facilitator@example.com", password="supersecret123")
        import uuid
        self.other_user = User.objects.create_user(name="Guest", email=f"guest-{uuid.uuid4()}@example.com", password="supersecret123")
        self.client.force_authenticate(self.user)

    def create_retrospective(self, status=RetrospectiveStatus.SETUP):
        retro = Retrospective.objects.create(
            title="Sprint 3 Retro",
            team_key="platform-team",
            facilitator=self.user,
            status=status,
        )
        Participant.objects.create(retrospective=retro, user=self.user, votes_remaining=3)
        return retro

    def test_facilitator_can_create_milestone_in_setup(self):
        retro = self.create_retrospective()
        url = f"/api/retrospectives/{retro.id}/milestones/"
        data = {"category": MilestoneCategory.ACHIEVEMENT, "description": "Entregamos o MVP!"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Milestone.objects.filter(retrospective=retro).count(), 1)

    def test_facilitator_cannot_create_milestone_outside_setup(self):
        retro = self.create_retrospective(status=RetrospectiveStatus.BOARD)
        url = f"/api/retrospectives/{retro.id}/milestones/"
        data = {"category": MilestoneCategory.ACHIEVEMENT, "description": "Fora da fase!"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_facilitator_cannot_create_milestone(self):
        retro = self.create_retrospective()
        self.client.force_authenticate(self.other_user)
        url = f"/api/retrospectives/{retro.id}/milestones/"
        data = {"category": MilestoneCategory.ACHIEVEMENT, "description": "Tentativa inválida"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(self.user)

    def test_list_milestones(self):
        retro = self.create_retrospective()
        Milestone.objects.create(retrospective=retro, author=self.user, category=MilestoneCategory.ACHIEVEMENT, description="Primeira")
        Milestone.objects.create(retrospective=retro, author=self.user, category=MilestoneCategory.CHALLENGE, description="Segunda")
        url = f"/api/retrospectives/{retro.id}/milestones/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_facilitator_can_update_and_delete_milestone_in_setup(self):
        retro = self.create_retrospective()
        milestone = Milestone.objects.create(retrospective=retro, author=self.user, category=MilestoneCategory.ACHIEVEMENT, description="Editar")
        url = f"/api/retrospectives/{retro.id}/milestones/{milestone.id}/"
        # Update
        response = self.client.patch(url, {"description": "Atualizado"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        milestone.refresh_from_db()
        self.assertEqual(milestone.description, "Atualizado")
        # Delete
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Milestone.objects.filter(id=milestone.id).exists())

    def test_facilitator_cannot_update_or_delete_milestone_outside_setup(self):
        retro = self.create_retrospective(status=RetrospectiveStatus.BOARD)
        milestone = Milestone.objects.create(retrospective=retro, author=self.user, category=MilestoneCategory.ACHIEVEMENT, description="Editar")
        url = f"/api/retrospectives/{retro.id}/milestones/{milestone.id}/"
        response = self.client.patch(url, {"description": "Atualizado"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_facilitator_cannot_update_or_delete_milestone(self):
        retro = self.create_retrospective()
        milestone = Milestone.objects.create(retrospective=retro, author=self.user, category=MilestoneCategory.ACHIEVEMENT, description="Editar")
        self.client.force_authenticate(self.other_user)
        url = f"/api/retrospectives/{retro.id}/milestones/{milestone.id}/"
        response = self.client.patch(url, {"description": "Atualizado"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
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