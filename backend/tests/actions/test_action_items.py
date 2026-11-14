import importlib
from datetime import timedelta

from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.actions.models import ActionItem, ActionItemStatus
from apps.cards.models import Card
from apps.retrospectives.models import Participant, Retrospective, RetrospectiveStatus

User = get_user_model()


class ActionItemApiTests(APITestCase):
	def setUp(self):
		self.facilitator = User.objects.create_user(name="Facilitator", email="facilitator-actions@example.com", password="supersecret123")
		self.participant_user = User.objects.create_user(name="Participant", email="participant-actions@example.com", password="supersecret123")
		self.outsider = User.objects.create_user(name="Outsider", email="outsider-actions@example.com", password="supersecret123")
		self.retrospective = Retrospective.objects.create(
			title="Sprint 5",
			team_key="platform-team",
			facilitator=self.facilitator,
			status=RetrospectiveStatus.DISCUSSION,
		)
		self.facilitator_participant = Participant.objects.create(retrospective=self.retrospective, user=self.facilitator, votes_remaining=3)
		self.assignee_participant = Participant.objects.create(retrospective=self.retrospective, user=self.participant_user, votes_remaining=3)
		self.card = Card.objects.create(retrospective=self.retrospective, author=self.facilitator, column="loathed", content="Foco")
		self.client.force_authenticate(self.facilitator)

	def test_facilitator_can_create_action_item(self):
		url = f"/api/retrospectives/{self.retrospective.id}/action-items/"

		response = self.client.post(
			url,
			{
				"description": "Criar playbook de incidentes.",
				"assignee_id": str(self.assignee_participant.id),
				"due_date": "2026-05-30",
				"card_id": str(self.card.id),
				"external_tracker_url": "https://github.com/diniz-prj/retroapp4l/issues/12",
			},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		action_item = ActionItem.objects.get(id=response.data["id"])
		self.assertEqual(action_item.assignee, self.participant_user)
		self.assertEqual(action_item.card, self.card)
		self.assertEqual(action_item.status, ActionItemStatus.NOT_STARTED)

	def test_action_item_requires_discussion_phase_for_create(self):
		self.retrospective.status = RetrospectiveStatus.ACTIONS
		self.retrospective.save(update_fields=["status"])
		url = f"/api/retrospectives/{self.retrospective.id}/action-items/"

		response = self.client.post(
			url,
			{
				"description": "Não deveria criar.",
				"assignee_id": str(self.assignee_participant.id),
			},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_participant_cannot_create_action_item(self):
		self.client.force_authenticate(self.participant_user)
		url = f"/api/retrospectives/{self.retrospective.id}/action-items/"

		response = self.client.post(
			url,
			{
				"description": "Participante não deve criar.",
				"assignee_id": str(self.assignee_participant.id),
			},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_participant_cannot_update_or_delete_action_item(self):
		action_item = ActionItem.objects.create(
			retrospective=self.retrospective,
			description="Acompanhar rollback.",
			assignee=self.participant_user,
			card=self.card,
		)
		url = f"/api/retrospectives/{self.retrospective.id}/action-items/{action_item.id}/"
		self.client.force_authenticate(self.participant_user)

		response = self.client.patch(
			url,
			{
				"description": "Acompanhar rollback e documentar.",
				"assignee_id": str(self.facilitator_participant.id),
				"status": ActionItemStatus.IN_PROGRESS,
			},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

		response = self.client.delete(url)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertTrue(ActionItem.objects.filter(id=action_item.id).exists())

	def test_facilitator_can_update_and_delete_action_item(self):
		action_item = ActionItem.objects.create(
			retrospective=self.retrospective,
			description="Acompanhar rollback.",
			assignee=self.participant_user,
			card=self.card,
		)
		url = f"/api/retrospectives/{self.retrospective.id}/action-items/{action_item.id}/"

		response = self.client.patch(
			url,
			{
				"description": "Acompanhar rollback e documentar.",
				"assignee_id": str(self.facilitator_participant.id),
				"status": ActionItemStatus.IN_PROGRESS,
			},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		action_item.refresh_from_db()
		self.assertEqual(action_item.assignee, self.facilitator)
		self.assertEqual(action_item.status, ActionItemStatus.IN_PROGRESS)

		response = self.client.delete(url)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(ActionItem.objects.filter(id=action_item.id).exists())

	def _create_closed_retrospective(self, title, closed_at, team_key="platform-team"):
		retro = Retrospective.objects.create(
			title=title,
			team_key=team_key,
			facilitator=self.facilitator,
			status=RetrospectiveStatus.CLOSED,
			closed_at=closed_at,
		)
		Participant.objects.create(retrospective=retro, user=self.facilitator, votes_remaining=3)
		retro.refresh_from_db()
		return retro

	def _previous_actions_url(self):
		return f"/api/retrospectives/{self.retrospective.id}/previous-actions/"

	def test_previous_actions_aggregates_pending_from_all_closed_retrospectives(self):
		older_retro = self._create_closed_retrospective("Sprint 4", "2026-04-01T12:00:00Z")
		latest_retro = self._create_closed_retrospective("Sprint 4.1", "2026-04-10T12:00:00Z")
		other_team = self._create_closed_retrospective("Outra equipe", "2026-04-15T12:00:00Z", team_key="other-team")

		older_pending = ActionItem.objects.create(
			retrospective=older_retro, description="Antiga pendente", assignee=self.facilitator
		)
		older_done = ActionItem.objects.create(
			retrospective=older_retro,
			description="Antiga concluída",
			assignee=self.facilitator,
			status=ActionItemStatus.DONE,
		)
		latest_pending = ActionItem.objects.create(
			retrospective=latest_retro,
			description="Recente em andamento",
			assignee=self.participant_user,
			status=ActionItemStatus.IN_PROGRESS,
		)
		ActionItem.objects.create(retrospective=other_team, description="Ignorar", assignee=self.facilitator)

		response = self.client.get(self._previous_actions_url())

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		# Contract change: no singular retrospective_id any more.
		self.assertNotIn("retrospective_id", response.data)
		self.assertEqual(
			[item["id"] for item in response.data["action_items"]],
			[str(older_pending.id), str(latest_pending.id)],
		)
		self.assertNotIn(str(older_done.id), [item["id"] for item in response.data["action_items"]])
		self.assertIn("status_updated_at", response.data["action_items"][0])

	def test_recently_completed_contains_done_items_updated_after_latest_closed_retro(self):
		older_retro = self._create_closed_retrospective("Sprint 4", "2026-04-01T12:00:00Z")
		self._create_closed_retrospective("Sprint 4.1", "2026-04-10T12:00:00Z")

		done_item = ActionItem.objects.create(
			retrospective=older_retro,
			description="Entregue depois do fechamento",
			assignee=self.facilitator,
			status=ActionItemStatus.DONE,
		)

		response = self.client.get(self._previous_actions_url())

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual([item["id"] for item in response.data["recently_completed"]], [str(done_item.id)])
		self.assertEqual(response.data["action_items"], [])

	def test_recently_completed_ignores_done_items_updated_before_latest_closed_retro(self):
		older_retro = self._create_closed_retrospective("Sprint 4", "2026-04-01T12:00:00Z")
		latest_retro = self._create_closed_retrospective("Sprint 4.1", "2026-04-10T12:00:00Z")
		done_item = ActionItem.objects.create(
			retrospective=older_retro,
			description="Concluída antes da última retro",
			assignee=self.facilitator,
			status=ActionItemStatus.DONE,
		)
		# Simula o estado gravado pelo backfill: conclusão anterior ao corte temporal.
		ActionItem.objects.filter(pk=done_item.pk).update(
			status_updated_at=latest_retro.closed_at - timedelta(days=1)
		)

		response = self.client.get(self._previous_actions_url())

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["recently_completed"], [])
		self.assertEqual(response.data["action_items"], [])

	def test_reopening_done_previous_action_returns_it_to_pending_list(self):
		older_retro = self._create_closed_retrospective("Sprint 4", "2026-04-01T12:00:00Z")
		self._create_closed_retrospective("Sprint 4.1", "2026-04-10T12:00:00Z")
		done_item = ActionItem.objects.create(
			retrospective=older_retro,
			description="Marcada como done por engano",
			assignee=self.facilitator,
			status=ActionItemStatus.DONE,
		)
		previous_status_updated_at = done_item.status_updated_at
		url = f"/api/retrospectives/{self.retrospective.id}/previous-actions/{done_item.id}/status/"

		response = self.client.put(url, {"status": ActionItemStatus.IN_PROGRESS}, format="json")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		done_item.refresh_from_db()
		self.assertEqual(done_item.status, ActionItemStatus.IN_PROGRESS)
		self.assertGreater(done_item.status_updated_at, previous_status_updated_at)

		response = self.client.get(self._previous_actions_url())
		self.assertEqual([item["id"] for item in response.data["action_items"]], [str(done_item.id)])
		self.assertEqual(response.data["recently_completed"], [])

	def test_previous_actions_without_closed_retrospective_returns_empty_lists(self):
		url = f"/api/retrospectives/{self.retrospective.id}/previous-actions/"

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data, {"action_items": [], "recently_completed": []})

	def test_backfill_sets_status_updated_at_from_created_at(self):
		legacy_item = ActionItem.objects.create(
			retrospective=self.retrospective,
			description="Registro legado",
			assignee=self.facilitator,
		)
		# Estado de uma linha criada antes da coluna existir.
		ActionItem.objects.filter(pk=legacy_item.pk).update(status_updated_at=None)
		migration = importlib.import_module("apps.actions.migrations.0004_actionitem_status_updated_at")

		migration.backfill_status_updated_at(django_apps, None)

		legacy_item.refresh_from_db()
		self.assertIsNotNone(legacy_item.status_updated_at)
		self.assertEqual(legacy_item.status_updated_at, legacy_item.created_at)

	def test_previous_action_status_update_accepts_not_started_alias(self):
		previous_retro = Retrospective.objects.create(
			title="Sprint 4",
			team_key="platform-team",
			facilitator=self.facilitator,
			status=RetrospectiveStatus.CLOSED,
			closed_at="2026-04-10T12:00:00Z",
		)
		Participant.objects.create(retrospective=previous_retro, user=self.facilitator, votes_remaining=3)
		action_item = ActionItem.objects.create(
			retrospective=previous_retro,
			description="Documentar decisão.",
			assignee=self.facilitator,
		)
		url = f"/api/retrospectives/{self.retrospective.id}/previous-actions/{action_item.id}/status/"

		response = self.client.put(url, {"status": "pending"}, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		action_item.refresh_from_db()
		self.assertEqual(action_item.status, ActionItemStatus.NOT_STARTED)

	def test_non_participant_cannot_access_action_items(self):
		self.client.force_authenticate(self.outsider)
		url = f"/api/retrospectives/{self.retrospective.id}/action-items/"

		response = self.client.get(url)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
