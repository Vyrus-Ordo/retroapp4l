"""Testes da Actions Review (spec `docs/specs/ActionsReview/spec.md`, seção 6 — backend)."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.actions.models import ActionItem, ActionItemStatus
from apps.cards.models import Card
from apps.retrospectives.models import Participant, Retrospective, RetrospectiveStatus

User = get_user_model()

TEAM = "platform"
OTHER_TEAM = "billing"


class ActionsReviewTestBase(APITestCase):
    """Factories mínimas no estilo dos testes vizinhos (APITestCase + force_authenticate)."""

    def setUp(self):
        self.facilitator = User.objects.create_user(
            name="Facilitator", email="facilitator-review@example.com", password="supersecret123"
        )
        self.member = User.objects.create_user(
            name="Member", email="member-review@example.com", password="supersecret123"
        )
        self.other_member = User.objects.create_user(
            name="Other Member", email="other-member-review@example.com", password="supersecret123"
        )
        self.outsider = User.objects.create_user(
            name="Outsider", email="outsider-review@example.com", password="supersecret123"
        )
        self.other_facilitator = User.objects.create_user(
            name="Other Facilitator", email="other-facilitator-review@example.com", password="supersecret123"
        )
        self.guest = User.objects.create_user(
            name="Guest", email="guest-review@example.com", password="supersecret123", is_guest=True
        )

        self.closed_retro = self.make_retro(
            status=RetrospectiveStatus.CLOSED,
            closed_at=timezone.now() - timedelta(days=10),
            participants=[self.member, self.other_member],
        )
        self.other_team_retro = self.make_retro(
            team_key=OTHER_TEAM,
            facilitator=self.other_facilitator,
            status=RetrospectiveStatus.CLOSED,
            closed_at=timezone.now() - timedelta(days=3),
            participants=[self.other_facilitator],
        )

        self.list_url = "/api/actions/"
        self.teams_url = "/api/actions/teams/"

    # -- factories ---------------------------------------------------------

    def make_retro(
        self,
        team_key=TEAM,
        facilitator=None,
        status=RetrospectiveStatus.CLOSED,
        closed_at=None,
        participants=(),
        title="Sprint",
        sprint_name="S1",
    ):
        retro = Retrospective.objects.create(
            title=title,
            sprint_name=sprint_name,
            team_key=team_key,
            facilitator=facilitator or self.facilitator,
            status=status,
            closed_at=closed_at,
        )
        seen = set()
        for user in [retro.facilitator, *participants]:
            if user.pk in seen:
                continue
            seen.add(user.pk)
            Participant.objects.create(retrospective=retro, user=user, votes_remaining=3)
        return retro

    def make_action(
        self,
        retrospective=None,
        assignee=None,
        description="Action",
        status_value=ActionItemStatus.NOT_STARTED,
        due_date=None,
        card=None,
        external_tracker_url="",
    ):
        return ActionItem.objects.create(
            retrospective=retrospective or self.closed_retro,
            assignee=assignee or self.member,
            description=description,
            status=status_value,
            due_date=due_date,
            card=card,
            external_tracker_url=external_tracker_url,
        )

    def detail_url(self, action):
        return f"/api/actions/{action.id}/"

    def results(self, response):
        return response.data["results"]


class ActionsReviewAccessTests(ActionsReviewTestBase):
    def test_list_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_member_sees_actions_of_own_team(self):
        action = self.make_action()
        self.client.force_authenticate(self.member)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(self.results(response)[0]["id"], str(action.id))

    def test_outsider_gets_empty_list(self):
        self.make_action()
        self.client.force_authenticate(self.outsider)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(self.results(response), [])

    def test_outsider_gets_404_on_detail(self):
        action = self.make_action()
        self.client.force_authenticate(self.outsider)

        response = self.client.get(self.detail_url(action))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_facilitator_of_another_team_gets_404_on_detail(self):
        action = self.make_action()
        self.client.force_authenticate(self.other_facilitator)

        response = self.client.get(self.detail_url(action))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_facilitator_of_another_team_cannot_patch_foreign_action(self):
        action = self.make_action()
        self.client.force_authenticate(self.other_facilitator)

        response = self.client.patch(self.detail_url(action), {"description": "Hack"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_gets_403_on_all_endpoints(self):
        action = self.make_action()
        self.client.force_authenticate(self.guest)

        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get(self.teams_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            self.client.get(self.detail_url(action)).status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            self.client.patch(self.detail_url(action), {"description": "x"}, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_participant_reads_but_cannot_edit(self):
        action = self.make_action()
        self.client.force_authenticate(self.member)

        self.assertEqual(self.client.get(self.detail_url(action)).status_code, status.HTTP_200_OK)
        response = self.client.patch(self.detail_url(action), {"description": "Changed"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        action.refresh_from_db()
        self.assertEqual(action.description, "Action")

    def test_facilitator_can_edit_action_of_closed_retrospective(self):
        action = self.make_action()
        self.client.force_authenticate(self.facilitator)

        response = self.client.patch(self.detail_url(action), {"description": "Changed"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        action.refresh_from_db()
        self.assertEqual(action.description, "Changed")
        self.assertTrue(response.data["can_edit"])

    def test_participant_sees_can_edit_false(self):
        action = self.make_action()
        self.client.force_authenticate(self.member)

        response = self.client.get(self.detail_url(action))

        self.assertFalse(response.data["can_edit"])


class ActionsReviewEditTests(ActionsReviewTestBase):
    def setUp(self):
        super().setUp()
        self.action = self.make_action(description="Original")
        self.client.force_authenticate(self.facilitator)

    def test_patch_on_active_retrospective_is_403(self):
        active = self.make_retro(status=RetrospectiveStatus.ACTIONS, participants=[self.member])
        action = self.make_action(retrospective=active, description="Live action")

        response = self.client.patch(self.detail_url(action), {"description": "Nope"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Edit this action inside the retrospective", str(response.data["detail"]))
        action.refresh_from_db()
        self.assertEqual(action.description, "Live action")

    def test_card_and_retrospective_are_ignored(self):
        card = Card.objects.create(
            retrospective=self.closed_retro, author=self.member, column="loathed", content="Card"
        )
        other_retro = self.make_retro(team_key=OTHER_TEAM)

        response = self.client.patch(
            self.detail_url(self.action),
            {
                "description": "Kept card",
                "card": str(card.id),
                "retrospective": str(other_retro.id),
                "id": "11111111-1111-1111-1111-111111111111",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.action.refresh_from_db()
        self.assertIsNone(self.action.card)
        self.assertEqual(self.action.retrospective, self.closed_retro)
        self.assertEqual(self.action.description, "Kept card")

    def test_assignee_from_another_retrospective_is_400(self):
        foreign_participant = Participant.objects.get(
            retrospective=self.other_team_retro, user=self.other_facilitator
        )

        response = self.client.patch(
            self.detail_url(self.action), {"assignee_id": str(foreign_participant.id)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            [str(detail) for detail in response.data["assignee_id"]],
            ["Assignee must be a participant in this retrospective."],
        )

    def test_assignee_id_moves_assignee_within_originating_retro(self):
        participant = Participant.objects.get(retrospective=self.closed_retro, user=self.other_member)

        response = self.client.patch(
            self.detail_url(self.action), {"assignee_id": str(participant.id)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.action.refresh_from_db()
        self.assertEqual(self.action.assignee, self.other_member)
        self.assertEqual(response.data["assignee_name"], "Other Member")
        self.assertEqual(response.data["assignee_user_id"], str(self.other_member.id))

    def test_due_date_null_clears_deadline(self):
        self.action.due_date = timezone.localdate() + timedelta(days=5)
        self.action.save()

        response = self.client.patch(self.detail_url(self.action), {"due_date": None}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.action.refresh_from_db()
        self.assertIsNone(self.action.due_date)
        self.assertIsNone(response.data["due_date"])

    def test_blank_description_is_400(self):
        for value in ("", "   "):
            with self.subTest(value=value):
                response = self.client.patch(
                    self.detail_url(self.action), {"description": value}, format="json"
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("description", response.data)

    def test_legacy_pending_status_alias_is_rejected(self):
        response = self.client.patch(self.detail_url(self.action), {"status": "pending"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)

    def test_valid_statuses_are_accepted(self):
        for value in (ActionItemStatus.IN_PROGRESS, ActionItemStatus.DONE, ActionItemStatus.NOT_STARTED):
            with self.subTest(value=value):
                response = self.client.patch(
                    self.detail_url(self.action), {"status": value}, format="json"
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.action.refresh_from_db()
                self.assertEqual(self.action.status, value)

    def test_external_tracker_url_is_editable(self):
        response = self.client.patch(
            self.detail_url(self.action),
            {"external_tracker_url": "https://github.com/diniz-prj/retroapp4l/issues/99"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.action.refresh_from_db()
        self.assertEqual(
            self.action.external_tracker_url, "https://github.com/diniz-prj/retroapp4l/issues/99"
        )

    def test_write_methods_do_not_exist(self):
        self.assertEqual(
            self.client.post(self.list_url, {"description": "new"}, format="json").status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertEqual(
            self.client.post(self.teams_url, {}, format="json").status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertEqual(
            self.client.put(self.detail_url(self.action), {"description": "x"}, format="json").status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertEqual(
            self.client.delete(self.detail_url(self.action)).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertTrue(ActionItem.objects.filter(id=self.action.id).exists())

    def test_detail_exposes_assignee_options_of_originating_retro(self):
        response = self.client.get(self.detail_url(self.action))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = {option["name"] for option in response.data["assignee_options"]}
        self.assertEqual(names, {"Facilitator", "Member", "Other Member"})
        participant_ids = {option["participant_id"] for option in response.data["assignee_options"]}
        self.assertEqual(
            participant_ids,
            {str(p.id) for p in Participant.objects.filter(retrospective=self.closed_retro)},
        )


class ActionsReviewFilterTests(ActionsReviewTestBase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(self.facilitator)
        today = timezone.localdate()

        self.overdue_open = self.make_action(
            description="Deploy pipeline",
            assignee=self.member,
            due_date=today - timedelta(days=3),
        )
        self.overdue_done = self.make_action(
            description="Old release",
            assignee=self.member,
            status_value=ActionItemStatus.DONE,
            due_date=today - timedelta(days=30),
        )
        self.upcoming = self.make_action(
            description="Write runbook",
            assignee=self.other_member,
            status_value=ActionItemStatus.IN_PROGRESS,
            due_date=today + timedelta(days=5),
        )
        self.no_deadline = self.make_action(description="Backlog cleanup", assignee=self.other_member)

        self.billing_retro = self.make_retro(
            team_key=OTHER_TEAM, facilitator=self.facilitator, participants=[self.member]
        )
        self.billing_action = self.make_action(
            retrospective=self.billing_retro, description="Billing invoice retry", assignee=self.member
        )

    def ids(self, response):
        return [item["id"] for item in self.results(response)]

    def test_team_key_single(self):
        response = self.client.get(self.list_url, {"team_key": TEAM})

        self.assertEqual(response.data["count"], 4)
        self.assertNotIn(str(self.billing_action.id), self.ids(response))

    def test_team_key_multiple(self):
        response = self.client.get(self.list_url, {"team_key": [TEAM, OTHER_TEAM]})

        self.assertEqual(response.data["count"], 5)
        self.assertIn(str(self.billing_action.id), self.ids(response))

    def test_team_key_outside_readable_is_ignored(self):
        response = self.client.get(self.list_url, {"team_key": ["does-not-exist"]})

        self.assertEqual(response.data["count"], 5)

    def test_status_single_and_multiple(self):
        response = self.client.get(self.list_url, {"status": ActionItemStatus.DONE})
        self.assertEqual([item["id"] for item in self.results(response)], [str(self.overdue_done.id)])

        response = self.client.get(
            self.list_url, {"status": [ActionItemStatus.NOT_STARTED, ActionItemStatus.IN_PROGRESS]}
        )
        self.assertEqual(response.data["count"], 4)

    def test_invalid_status_is_400(self):
        response = self.client.get(self.list_url, {"status": "pending"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)

    def test_assignee_me(self):
        response = self.client.get(self.list_url, {"assignee": "me"})

        # O facilitador não é responsável por nenhuma ação semeada.
        self.assertEqual(response.data["count"], 0)

    def test_assignee_by_user_id(self):
        response = self.client.get(self.list_url, {"assignee": str(self.member.id)})

        self.assertEqual(response.data["count"], 3)

    def test_assignee_invalid_uuid_is_400(self):
        response = self.client.get(self.list_url, {"assignee": "not-a-uuid"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_overdue_excludes_done(self):
        response = self.client.get(self.list_url, {"overdue": "true"})

        self.assertEqual([item["id"] for item in self.results(response)], [str(self.overdue_open.id)])
        self.assertTrue(self.results(response)[0]["is_overdue"])

    def test_due_before_and_due_after_are_inclusive(self):
        response = self.client.get(self.list_url, {"due_before": str(self.overdue_open.due_date)})
        self.assertEqual(
            {item["id"] for item in self.results(response)},
            {str(self.overdue_open.id), str(self.overdue_done.id)},
        )

        response = self.client.get(self.list_url, {"due_after": str(self.upcoming.due_date)})
        self.assertEqual([item["id"] for item in self.results(response)], [str(self.upcoming.id)])

    def test_due_date_filter_rejects_bad_format(self):
        response = self.client.get(self.list_url, {"due_before": "14/11/2026"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_query_matches_description(self):
        response = self.client.get(self.list_url, {"q": "runbook"})

        self.assertEqual([item["id"] for item in self.results(response)], [str(self.upcoming.id)])

    def test_default_ordering_by_due_date_with_nulls_last(self):
        response = self.client.get(self.list_url)

        self.assertEqual(
            self.ids(response),
            [
                str(self.overdue_done.id),
                str(self.overdue_open.id),
                str(self.upcoming.id),
                str(self.no_deadline.id),
                str(self.billing_action.id),
            ],
        )

    def test_descending_ordering_keeps_nulls_last(self):
        response = self.client.get(self.list_url, {"ordering": "-due_date"})

        self.assertEqual(
            self.ids(response),
            [
                str(self.upcoming.id),
                str(self.overdue_open.id),
                str(self.overdue_done.id),
                str(self.no_deadline.id),
                str(self.billing_action.id),
            ],
        )

    def test_ordering_tie_is_broken_by_retrospective_closed_at(self):
        due_date = timezone.localdate() + timedelta(days=1)
        older_retro = self.make_retro(
            status=RetrospectiveStatus.CLOSED,
            closed_at=timezone.now() - timedelta(days=60),
        )
        newer_retro = self.make_retro(
            status=RetrospectiveStatus.CLOSED,
            closed_at=timezone.now() - timedelta(days=5),
        )
        older_action = self.make_action(
            retrospective=older_retro, description="Tie older", due_date=due_date
        )
        newer_action = self.make_action(
            retrospective=newer_retro, description="Tie newer", due_date=due_date
        )

        response = self.client.get(self.list_url, {"due_before": str(due_date), "due_after": str(due_date)})

        self.assertEqual(self.ids(response), [str(older_action.id), str(newer_action.id)])

    def test_ordering_created_at_is_supported(self):
        response = self.client.get(self.list_url, {"ordering": "-created_at"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.results(response)[0]["id"], str(self.billing_action.id))

    def test_invalid_ordering_falls_back_to_default(self):
        response = self.client.get(self.list_url, {"ordering": "nonsense"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(self.results(response)[-1]["due_date"])


class ActionsReviewPaginationTests(ActionsReviewTestBase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(self.facilitator)
        ActionItem.objects.bulk_create(
            [
                ActionItem(
                    retrospective=self.closed_retro,
                    assignee=self.member,
                    description=f"Bulk action {index}",
                )
                for index in range(105)
            ]
        )

    def test_default_page_size_is_25(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.data["count"], 105)
        self.assertEqual(len(self.results(response)), 25)
        self.assertIsNotNone(response.data["next"])

    def test_page_size_is_honoured_up_to_100(self):
        response = self.client.get(self.list_url, {"page_size": 10})
        self.assertEqual(len(self.results(response)), 10)

        response = self.client.get(self.list_url, {"page_size": 100})
        self.assertEqual(len(self.results(response)), 100)

        response = self.client.get(self.list_url, {"page_size": 1000})
        self.assertEqual(len(self.results(response)), 100)

    def test_second_page_continues_the_result_set(self):
        first = self.client.get(self.list_url, {"page_size": 50})
        second = self.client.get(self.list_url, {"page_size": 50, "page": 2})

        first_ids = {item["id"] for item in first.data["results"]}
        second_ids = {item["id"] for item in second.data["results"]}

        self.assertEqual(len(first_ids & second_ids), 0)
        self.assertEqual(len(first_ids | second_ids), 100)


class ActionsReviewTeamsTests(ActionsReviewTestBase):
    def test_teams_expose_counts_and_can_edit(self):
        # platform: `member` é apenas participante do time.
        self.make_action(status_value=ActionItemStatus.NOT_STARTED)
        self.make_action(status_value=ActionItemStatus.DONE)
        second_retro = self.make_retro(participants=[self.member])
        self.make_action(retrospective=second_retro, status_value=ActionItemStatus.IN_PROGRESS)
        # billing: `member` é facilitador do time.
        billing_retro = self.make_retro(
            team_key=OTHER_TEAM,
            facilitator=self.member,
            participants=[self.other_member],
        )
        self.make_action(
            retrospective=billing_retro,
            assignee=self.other_member,
            status_value=ActionItemStatus.NOT_STARTED,
        )

        self.client.force_authenticate(self.member)
        response = self.client.get(self.teams_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                {"team_key": OTHER_TEAM, "pending": 1, "total": 1, "can_edit": True},
                {"team_key": TEAM, "pending": 2, "total": 3, "can_edit": False},
            ],
        )

    def test_teams_only_lists_readable_teams_for_participant(self):
        self.make_action()
        self.client.force_authenticate(self.member)

        response = self.client.get(self.teams_url)

        self.assertEqual([row["team_key"] for row in response.data], [TEAM])
        self.assertFalse(response.data[0]["can_edit"])

    def test_teams_empty_for_outsider(self):
        self.make_action()
        self.client.force_authenticate(self.outsider)

        response = self.client.get(self.teams_url)

        self.assertEqual(response.data, [])


class ActionsReviewEffectsTests(ActionsReviewTestBase):
    def test_done_updates_status_updated_at_and_feeds_next_check_phase(self):
        action = self.make_action(status_value=ActionItemStatus.IN_PROGRESS)
        previous_timestamp = action.status_updated_at
        check_retro = self.make_retro(
            status=RetrospectiveStatus.CHECK, participants=[self.facilitator, self.member]
        )

        self.client.force_authenticate(self.facilitator)
        response = self.client.patch(
            self.detail_url(action), {"status": ActionItemStatus.DONE}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        action.refresh_from_db()
        self.assertEqual(action.status, ActionItemStatus.DONE)
        self.assertGreater(action.status_updated_at, previous_timestamp)

        check_response = self.client.get(
            f"/api/retrospectives/{check_retro.id}/previous-actions/"
        )

        self.assertEqual(check_response.status_code, status.HTTP_200_OK)
        completed_ids = [item["id"] for item in check_response.data["recently_completed"]]
        self.assertIn(str(action.id), completed_ids)
        pending_ids = [item["id"] for item in check_response.data["action_items"]]
        self.assertNotIn(str(action.id), pending_ids)

    def test_patch_without_status_change_keeps_status_updated_at(self):
        action = self.make_action()
        previous_timestamp = action.status_updated_at
        self.client.force_authenticate(self.facilitator)

        response = self.client.patch(
            self.detail_url(action), {"description": "Only text"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        action.refresh_from_db()
        self.assertEqual(action.status_updated_at, previous_timestamp)


class ActionsReviewAnonymityTests(ActionsReviewTestBase):
    def test_payload_never_exposes_card_content_or_author(self):
        card = Card.objects.create(
            retrospective=self.closed_retro,
            author=self.member,
            column="loathed",
            content="Segredo do card anônimo",
            is_anonymous=True,
        )
        self.make_action(card=card, description="Anonymous origin")
        self.client.force_authenticate(self.facilitator)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.data["results"][0]
        self.assertNotIn("card", payload)
        self.assertNotIn("card_id", payload)
        self.assertNotIn("author", payload)
        self.assertNotIn("author_name", payload)
        self.assertNotIn("Segredo do card anônimo", str(response.data))


class ActionsReviewAssigneeParticipantTests(ActionsReviewTestBase):
    """Emenda de 2026-11-14 (spec §3.1): `assignee_participant_id`."""

    def test_list_exposes_participant_id_of_current_assignee(self):
        self.make_action(assignee=self.member)
        self.client.force_authenticate(self.facilitator)

        payload = self.results(self.client.get(self.list_url))[0]

        expected = Participant.objects.get(retrospective=self.closed_retro, user=self.member)
        self.assertEqual(payload["assignee_participant_id"], str(expected.id))
        self.assertEqual(payload["assignee_user_id"], str(self.member.id))

    def test_detail_exposes_participant_id_of_current_assignee(self):
        action = self.make_action(assignee=self.other_member)
        self.client.force_authenticate(self.facilitator)

        payload = self.client.get(self.detail_url(action)).data

        expected = Participant.objects.get(retrospective=self.closed_retro, user=self.other_member)
        self.assertEqual(payload["assignee_participant_id"], str(expected.id))

    def test_null_when_assignee_has_no_participant_record(self):
        action = self.make_action(assignee=self.outsider)
        self.client.force_authenticate(self.facilitator)

        list_payload = self.results(self.client.get(self.list_url))[0]
        detail_payload = self.client.get(self.detail_url(action)).data

        self.assertIsNone(list_payload["assignee_participant_id"])
        self.assertEqual(list_payload["assignee_name"], "Outsider")
        self.assertIsNone(detail_payload["assignee_participant_id"])

    def test_participant_id_follows_the_new_assignee_after_patch(self):
        action = self.make_action(assignee=self.member)
        new_participant = Participant.objects.get(retrospective=self.closed_retro, user=self.other_member)
        self.client.force_authenticate(self.facilitator)

        response = self.client.patch(
            self.detail_url(action), {"assignee_id": str(new_participant.id)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["assignee_participant_id"], str(new_participant.id))
        self.assertEqual(
            self.results(self.client.get(self.list_url))[0]["assignee_participant_id"],
            str(new_participant.id),
        )


class ActionsReviewQueryCountTests(ActionsReviewTestBase):
    def count_list_queries(self):
        with CaptureQueriesContext(connection) as captured:
            response = self.client.get(self.list_url, {"page_size": 100})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return len(captured.captured_queries)

    def test_list_query_count_does_not_grow_with_items(self):
        self.make_action()
        self.make_action(retrospective=self.make_retro(), description="Second")
        self.client.force_authenticate(self.facilitator)
        baseline = self.count_list_queries()
        # time legível + time editável + count da paginação + página + participantes da página
        self.assertLessEqual(baseline, 5)

        for index in range(8):
            self.make_action(description=f"Extra {index}")

        # `assignee_participant_id` vem de um mapa montado uma vez por página.
        self.assertEqual(self.count_list_queries(), baseline)
