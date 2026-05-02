import uuid

from django.conf import settings
from django.db import models

from apps.retrospectives.models import Retrospective


class CardColumn(models.TextChoices):
	LOVED = "loved", "Loved"
	LOATHED = "loathed", "Loathed"
	LONGED = "longed", "Longed for"
	LEARNED = "learned", "Learned"


class Card(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	retrospective = models.ForeignKey(Retrospective, on_delete=models.CASCADE, related_name="cards")
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cards")
	column = models.CharField(max_length=16, choices=CardColumn.choices)
	content = models.CharField(max_length=500)
	group = models.ForeignKey("self", on_delete=models.SET_NULL, related_name="grouped_cards", blank=True, null=True)
	position = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["column", "position", "created_at"]


class CardVote(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="votes")
	voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="card_votes")
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=("card", "voter"), name="unique_card_vote_per_voter"),
		]
		ordering = ["created_at"]

# Create your models here.
