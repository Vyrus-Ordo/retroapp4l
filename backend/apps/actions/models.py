import uuid

from django.conf import settings
from django.db import models

from apps.cards.models import Card
from apps.retrospectives.models import Retrospective


class ActionItemStatus(models.TextChoices):
	PENDING = "pending", "Pending"
	IN_PROGRESS = "in_progress", "In progress"
	DONE = "done", "Done"


class ActionItem(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	retrospective = models.ForeignKey(Retrospective, on_delete=models.CASCADE, related_name="action_items")
	card = models.ForeignKey(Card, on_delete=models.SET_NULL, related_name="action_items", blank=True, null=True)
	description = models.TextField()
	assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assigned_action_items")
	due_date = models.DateField(blank=True, null=True)
	status = models.CharField(max_length=20, choices=ActionItemStatus.choices, default=ActionItemStatus.PENDING)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["created_at"]

# Create your models here.
