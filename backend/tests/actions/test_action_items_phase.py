from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.actions.models import ActionItem
from apps.cards.models import Card
from apps.retrospectives.models import Participant, Retrospective, RetrospectiveStatus

User = get_user_model()

class ActionItemsPhaseTests(APITestCase):
	def setUp(self):
		self.facilitator = User.objects.create_user(name="Facilitator", email="fac@example.com", password="pass")
		self.participant_user = User.objects.create_user(name="Participant", email="par@example.com", password="pass")
		
		self.retrospective = Retrospective.objects.create(
			title="Test Sprint",
			team_key="test-team",
			facilitator=self.facilitator,
			status=RetrospectiveStatus.DISCUSSION,
		)
		self.facilitator_participant = Participant.objects.create(retrospective=self.retrospective, user=self.facilitator, votes_remaining=3)
		self.assignee_participant = Participant.objects.create(retrospective=self.retrospective, user=self.participant_user, votes_remaining=3)
		self.focus_card = Card.objects.create(retrospective=self.retrospective, author=self.facilitator, column="loathed", content="Foco")
		
		self.url = f"/api/retrospectives/{self.retrospective.id}/action-items/"

	def test_discussion_facilitator_can_create(self):
		self.client.force_authenticate(self.facilitator)
		response = self.client.post(self.url, {
			"description": "Fix the bug",
			"assignee_id": str(self.assignee_participant.id),
			"card_id": str(self.focus_card.id)
		}, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		action = ActionItem.objects.get(id=response.data["id"])
		self.assertEqual(action.card, self.focus_card)

	def test_discussion_participant_cannot_create(self):
		self.client.force_authenticate(self.participant_user)
		response = self.client.post(self.url, {
			"description": "Fix the bug",
			"assignee_id": str(self.assignee_participant.id),
		}, format="json")
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_actions_facilitator_cannot_create(self):
		self.retrospective.status = RetrospectiveStatus.ACTIONS
		self.retrospective.save()
		self.client.force_authenticate(self.facilitator)
		response = self.client.post(self.url, {
			"description": "Fix the bug",
			"assignee_id": str(self.assignee_participant.id),
		}, format="json")
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_actions_participant_cannot_create(self):
		self.retrospective.status = RetrospectiveStatus.ACTIONS
		self.retrospective.save()
		self.client.force_authenticate(self.participant_user)
		response = self.client.post(self.url, {
			"description": "Fix the bug",
			"assignee_id": str(self.assignee_participant.id),
		}, format="json")
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_actions_facilitator_can_edit(self):
		self.retrospective.status = RetrospectiveStatus.ACTIONS
		self.retrospective.save()
		action_item = ActionItem.objects.create(
			retrospective=self.retrospective,
			description="Original desc",
			assignee=self.participant_user,
		)
		self.client.force_authenticate(self.facilitator)
		url = f"{self.url}{action_item.id}/"
		
		response = self.client.patch(url, {
			"description": "New desc",
			"assignee_id": str(self.facilitator_participant.id),
			"due_date": "2026-10-10",
			"card_id": str(self.focus_card.id)
		}, format="json")
		
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		action_item.refresh_from_db()
		self.assertEqual(action_item.description, "New desc")
		self.assertEqual(action_item.assignee, self.facilitator)
		self.assertEqual(action_item.due_date.strftime("%Y-%m-%d"), "2026-10-10")
		self.assertEqual(action_item.card, self.focus_card)

	def test_actions_participant_cannot_edit(self):
		self.retrospective.status = RetrospectiveStatus.ACTIONS
		self.retrospective.save()
		action_item = ActionItem.objects.create(
			retrospective=self.retrospective,
			description="Original desc",
			assignee=self.participant_user,
		)
		self.client.force_authenticate(self.participant_user)
		url = f"{self.url}{action_item.id}/"
		
		response = self.client.patch(url, {"description": "New desc"}, format="json")
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_previous_phases_cannot_create(self):
		for phase in [RetrospectiveStatus.SETUP, RetrospectiveStatus.BOARD, RetrospectiveStatus.VOTING]:
			self.retrospective.status = phase
			self.retrospective.save()
			self.client.force_authenticate(self.facilitator)
			response = self.client.post(self.url, {
				"description": "Fix the bug",
				"assignee_id": str(self.assignee_participant.id),
			}, format="json")
			self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
