from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.actions.models import ActionItem, ActionItemStatus
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
        self.assertIsNotNone(retrospective.invite_token)
        self.assertTrue(
            Participant.objects.filter(retrospective=retrospective, user=self.user, votes_remaining=retrospective.max_votes_per_user).exists()
        )

    def test_detail_backfills_missing_invite_token_for_active_retro(self):
        retrospective = Retrospective.objects.create(
            title="Sprint 1 Retro",
            team_key="platform-team",
            facilitator=self.user,
            status=RetrospectiveStatus.LOBBY,
            invite_token=None,
        )
        Participant.objects.create(retrospective=retrospective, user=self.user, votes_remaining=3)

        response = self.client.get(f"/api/retrospectives/{retrospective.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        retrospective.refresh_from_db()
        self.assertIsNotNone(retrospective.invite_token)
        self.assertEqual(response.data["invite_token"], str(retrospective.invite_token))

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

    def test_history_lists_closed_retrospectives_with_counts(self):
        closed = Retrospective.objects.create(
            title="Closed Retro",
            team_key="platform-team",
            facilitator=self.user,
            status=RetrospectiveStatus.CLOSED,
            closed_at=timezone.now(),
        )
        Participant.objects.create(retrospective=closed, user=self.user, votes_remaining=3)
        ActionItem.objects.create(retrospective=closed, description="Uma ação", assignee=self.user, status=ActionItemStatus.DONE)

        response = self.client.get("/api/retrospectives/history/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(closed.id))
        self.assertEqual(response.data[0]["action_items_count"], 1)
        self.assertEqual(response.data[0]["action_item_status_summary"], {"not_started": 0, "in_progress": 0, "done": 1})

    def test_closed_detail_includes_cards_votes_milestones_and_action_items(self):
        closed = Retrospective.objects.create(
            title="Closed Retro",
            team_key="platform-team",
            facilitator=self.user,
            status=RetrospectiveStatus.CLOSED,
            closed_at=timezone.now(),
        )
        participant = Participant.objects.create(retrospective=closed, user=self.user, votes_remaining=3)
        milestone = Milestone.objects.create(retrospective=closed, author=self.user, category=MilestoneCategory.ACHIEVEMENT, description="Marco")
        from apps.cards.models import Card, CardVote

        card = Card.objects.create(retrospective=closed, author=self.user, column="loathed", content="Dor", is_anonymous=True)
        vote = CardVote.objects.create(card=card, voter=self.user)
        action_item = ActionItem.objects.create(retrospective=closed, description="Ação", assignee=self.user, card=card)

        response = self.client.get(f"/api/retrospectives/{closed.id}/detail/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["participants"][0]["id"], str(participant.id))
        self.assertEqual(response.data["milestones"][0]["id"], str(milestone.id))
        self.assertEqual(response.data["cards"][0]["id"], str(card.id))
        self.assertIsNone(response.data["cards"][0]["author"])
        self.assertIsNone(response.data["cards"][0]["author_name"])
        self.assertTrue(response.data["cards"][0]["is_anonymous"])
        self.assertEqual(response.data["votes"][0]["id"], str(vote.id))
        self.assertEqual(response.data["action_items"][0]["id"], str(action_item.id))

    def test_facilitator_can_focus_and_advance_discussion_card(self):
        retro = Retrospective.objects.create(
            title="Discussion Retro",
            team_key="platform-team",
            facilitator=self.user,
            status=RetrospectiveStatus.DISCUSSION,
        )
        Participant.objects.create(retrospective=retro, user=self.user, votes_remaining=3)
        from apps.cards.models import Card, CardVote

        card_one = Card.objects.create(retrospective=retro, author=self.user, column="loathed", content="Primeiro", is_anonymous=True)
        card_two = Card.objects.create(retrospective=retro, author=self.user, column="longed", content="Segundo")
        grouped_child = Card.objects.create(retrospective=retro, author=self.user, column="longed", content="Filho agrupado", group=card_two)
        other_user = User.objects.create_user(name="Voter", email="voter-focus@example.com", password="supersecret123")
        Participant.objects.create(retrospective=retro, user=other_user, votes_remaining=3)
        CardVote.objects.create(card=card_two, voter=other_user)
        CardVote.objects.create(card=grouped_child, voter=other_user)

        focus_response = self.client.post(
            f"/api/retrospectives/{retro.id}/focus-card/",
            {"card_id": str(card_one.id)},
            format="json",
        )
        self.assertEqual(focus_response.status_code, status.HTTP_200_OK)
        self.assertIsNone(focus_response.data["author"])
        self.assertEqual(focus_response.data["author_display"], "Anonymous")
        self.assertTrue(focus_response.data["is_anonymous"])
        retro.refresh_from_db()
        self.assertEqual(retro.focus_card_id, card_one.id)

        next_response = self.client.post(f"/api/retrospectives/{retro.id}/next-card/", format="json")
        self.assertEqual(next_response.status_code, status.HTTP_200_OK)
        self.assertEqual(next_response.data["card_id"], str(card_two.id))

    def test_facilitator_can_close_retrospective_from_actions_phase(self):
        retro = Retrospective.objects.create(
            title="Actions Retro",
            team_key="platform-team",
            facilitator=self.user,
            status=RetrospectiveStatus.ACTIONS,
            invite_token="11111111-1111-1111-1111-111111111111",
        )
        Participant.objects.create(retrospective=retro, user=self.user, votes_remaining=3)

        response = self.client.post(
            f"/api/retrospectives/{retro.id}/close/",
            {"confirm": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        retro.refresh_from_db()
        self.assertEqual(retro.status, RetrospectiveStatus.CLOSED)
        self.assertIsNotNone(retro.closed_at)
        self.assertIsNone(retro.invite_token)

    def test_close_requires_actions_phase(self):
        retro = self.create_retrospective(status=RetrospectiveStatus.DISCUSSION)

        response = self.client.post(
            f"/api/retrospectives/{retro.id}/close/",
            {"confirm": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
