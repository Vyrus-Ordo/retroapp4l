from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.cards.models import Card
from apps.retrospectives.models import Participant, Retrospective

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
