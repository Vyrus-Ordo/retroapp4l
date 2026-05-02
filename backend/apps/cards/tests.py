from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.cards.models import Card, CardVote
from apps.retrospectives.models import Participant, Retrospective, RetrospectiveStatus

User = get_user_model()

class CardCRUDTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user1@example.com", password="testpass", name="User 1")
        self.other_user = User.objects.create_user(email="user2@example.com", password="testpass", name="User 2")
        self.retrospective = Retrospective.objects.create(title="Sprint 3", team_key="team1", facilitator=self.user)
        Participant.objects.create(retrospective=self.retrospective, user=self.user, votes_remaining=3)
        self.cards_url = f"/api/retrospectives/{self.retrospective.id}/cards/"
        self.client.force_authenticate(user=self.user)

    def test_create_card(self):
        data = {"column": "loved", "content": "Ótimo trabalho!"}
        response = self.client.post(self.cards_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Card.objects.count(), 1)
        self.assertEqual(Card.objects.first().author, self.user)

    def test_list_cards(self):
        Card.objects.create(retrospective=self.retrospective, author=self.user, column="loved", content="A")
        Card.objects.create(retrospective=self.retrospective, author=self.user, column="loathed", content="B")
        response = self.client.get(self.cards_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_edit_card_by_author(self):
        card = Card.objects.create(retrospective=self.retrospective, author=self.user, column="loved", content="A")
        url = f"/api/retrospectives/{self.retrospective.id}/cards/{card.id}/"
        response = self.client.put(url, {"column": "loved", "content": "Editado"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        card.refresh_from_db()
        self.assertEqual(card.content, "Editado")

    def test_edit_card_by_other_user_forbidden(self):
        card = Card.objects.create(retrospective=self.retrospective, author=self.user, column="loved", content="A")
        url = f"/api/retrospectives/{self.retrospective.id}/cards/{card.id}/"
        self.client.force_authenticate(user=self.other_user)
        response = self.client.put(url, {"column": "loved", "content": "Hack"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_card_by_author(self):
        card = Card.objects.create(retrospective=self.retrospective, author=self.user, column="loved", content="A")
        url = f"/api/retrospectives/{self.retrospective.id}/cards/{card.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Card.objects.count(), 0)

    def test_delete_card_by_other_user_forbidden(self):
        card = Card.objects.create(retrospective=self.retrospective, author=self.user, column="loved", content="A")
        url = f"/api/retrospectives/{self.retrospective.id}/cards/{card.id}/"
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_content_length_limit(self):
        data = {"column": "loved", "content": "A" * 501}
        response = self.client.post(self.cards_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_participant_cannot_create_card(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(self.cards_url, {"column": "loved", "content": "Tentativa"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CardGroupingTests(APITestCase):
    def setUp(self):
        self.facilitator = User.objects.create_user(email="facilitator@example.com", password="testpass", name="Facilitator")
        self.participant = User.objects.create_user(email="participant@example.com", password="testpass", name="Participant")
        self.retrospective = Retrospective.objects.create(title="Sprint 4", team_key="team-group", facilitator=self.facilitator)
        Participant.objects.create(retrospective=self.retrospective, user=self.facilitator, votes_remaining=3)
        Participant.objects.create(retrospective=self.retrospective, user=self.participant, votes_remaining=3)
        self.card_a = Card.objects.create(retrospective=self.retrospective, author=self.facilitator, column="loathed", content="A")
        self.card_b = Card.objects.create(retrospective=self.retrospective, author=self.participant, column="loathed", content="B")
        self.card_c = Card.objects.create(retrospective=self.retrospective, author=self.participant, column="longed", content="C")
        self.group_url = f"/api/retrospectives/{self.retrospective.id}/cards/group/"
        self.client.force_authenticate(user=self.facilitator)

    def test_facilitator_can_group_cards_in_same_column(self):
        response = self.client.post(
            self.group_url,
            {"card_ids": [str(self.card_a.id), str(self.card_b.id)], "group_parent_id": str(self.card_a.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.card_b.refresh_from_db()
        self.assertEqual(self.card_b.group_id, self.card_a.id)

    def test_grouping_requires_same_column(self):
        response = self.client.post(
            self.group_url,
            {"card_ids": [str(self.card_a.id), str(self.card_c.id)]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_facilitator_can_group_cards(self):
        self.client.force_authenticate(user=self.participant)

        response = self.client.post(
            self.group_url,
            {"card_ids": [str(self.card_a.id), str(self.card_b.id)]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_facilitator_can_ungroup_card(self):
        self.card_b.group = self.card_a
        self.card_b.save(update_fields=["group"])
        ungroup_url = f"/api/retrospectives/{self.retrospective.id}/cards/{self.card_b.id}/ungroup/"

        response = self.client.post(ungroup_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.card_b.refresh_from_db()
        self.assertIsNone(self.card_b.group_id)


class CardVotingTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(email="author@example.com", password="testpass", name="Author")
        self.voter = User.objects.create_user(email="voter@example.com", password="testpass", name="Voter")
        self.other = User.objects.create_user(email="other@example.com", password="testpass", name="Other")
        self.retrospective = Retrospective.objects.create(
            title="Sprint 4 Votes",
            team_key="team-vote",
            facilitator=self.author,
            status=RetrospectiveStatus.VOTING,
            max_votes_per_user=3,
        )
        self.author_participant = Participant.objects.create(retrospective=self.retrospective, user=self.author, votes_remaining=3)
        self.voter_participant = Participant.objects.create(retrospective=self.retrospective, user=self.voter, votes_remaining=3)
        Participant.objects.create(retrospective=self.retrospective, user=self.other, votes_remaining=3)
        self.loathed_card = Card.objects.create(retrospective=self.retrospective, author=self.author, column="loathed", content="Pain")
        self.longed_card = Card.objects.create(retrospective=self.retrospective, author=self.author, column="longed", content="Wish")
        self.loved_card = Card.objects.create(retrospective=self.retrospective, author=self.other, column="loved", content="Love")
        self.vote_url = f"/api/retrospectives/{self.retrospective.id}/cards/{self.loathed_card.id}/vote/"
        self.votes_url = f"/api/retrospectives/{self.retrospective.id}/votes/"
        self.config_url = f"/api/retrospectives/{self.retrospective.id}/votes-config/"
        self.client.force_authenticate(user=self.voter)

    def test_participant_can_vote_on_loathed_card(self):
        response = self.client.post(self.vote_url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CardVote.objects.filter(card=self.loathed_card, voter=self.voter).exists())
        self.voter_participant.refresh_from_db()
        self.assertEqual(self.voter_participant.votes_remaining, 2)

    def test_participant_cannot_vote_on_own_card(self):
        self.client.force_authenticate(user=self.author)
        own_vote_url = f"/api/retrospectives/{self.retrospective.id}/cards/{self.loathed_card.id}/vote/"

        response = self.client.post(own_vote_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_participant_cannot_vote_on_non_votable_column(self):
        invalid_url = f"/api/retrospectives/{self.retrospective.id}/cards/{self.loved_card.id}/vote/"

        response = self.client.post(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_participant_cannot_vote_twice_on_same_card(self):
        self.client.post(self.vote_url)

        response = self.client.post(self.vote_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_participant_can_revoke_vote(self):
        self.client.post(self.vote_url)

        response = self.client.delete(self.vote_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CardVote.objects.filter(card=self.loathed_card, voter=self.voter).exists())
        self.voter_participant.refresh_from_db()
        self.assertEqual(self.voter_participant.votes_remaining, 3)

    def test_vote_list_returns_votes_for_retrospective(self):
        CardVote.objects.create(card=self.loathed_card, voter=self.voter)

        response = self.client.get(self.votes_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_facilitator_can_update_votes_config_before_voting(self):
        self.retrospective.status = RetrospectiveStatus.GROUPING
        self.retrospective.save(update_fields=["status"])
        self.client.force_authenticate(user=self.author)

        response = self.client.put(self.config_url, {"max_votes_per_user": 5}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.retrospective.refresh_from_db()
        self.voter_participant.refresh_from_db()
        self.assertEqual(self.retrospective.max_votes_per_user, 5)
        self.assertEqual(self.voter_participant.votes_remaining, 5)
