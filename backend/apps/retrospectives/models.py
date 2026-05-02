import uuid

from django.conf import settings
from django.db import models


class RetrospectiveStatus(models.TextChoices):
	SETUP = "setup", "Setup"
	LOBBY = "lobby", "Lobby"
	PRESENTATION = "presentation", "Presentation"
	CHECK = "check", "Check"
	BOARD = "board", "Board"
	GROUPING = "grouping", "Grouping"
	VOTING = "voting", "Voting"
	DISCUSSION = "discussion", "Discussion"
	ACTIONS = "actions", "Actions"
	CLOSED = "closed", "Closed"


class MilestoneCategory(models.TextChoices):
	ACHIEVEMENT = "achievement", "Achievement"
	CHALLENGE = "challenge", "Challenge"
	CHANGE = "change", "Change"
	RECOGNITION = "recognition", "Recognition"
	OTHER = "other", "Other"


class AccessLogAction(models.TextChoices):
	OPENED = "opened", "Opened"
	CLOSED = "closed", "Closed"
	PARTICIPANT_JOINED = "participant_joined", "Participant joined"


class Retrospective(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	title = models.CharField(max_length=255)
	sprint_name = models.CharField(max_length=255, blank=True, null=True)
	description = models.TextField(blank=True)
	team_key = models.SlugField(max_length=100)
	facilitator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="facilitated_retrospectives")
	status = models.CharField(max_length=20, choices=RetrospectiveStatus.choices, default=RetrospectiveStatus.SETUP)
	invite_token = models.UUIDField(unique=True, blank=True, null=True)
	invite_revoked_at = models.DateTimeField(blank=True, null=True)
	max_votes_per_user = models.PositiveSmallIntegerField(default=3)
	skip_check_phase = models.BooleanField(default=False)
	timer_started_at = models.DateTimeField(blank=True, null=True)
	timer_paused_at = models.DateTimeField(blank=True, null=True)
	timer_duration_seconds = models.PositiveIntegerField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	closed_at = models.DateTimeField(blank=True, null=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:
		return self.title


class Milestone(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	retrospective = models.ForeignKey(Retrospective, on_delete=models.CASCADE, related_name="milestones")
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="milestones")
	category = models.CharField(max_length=20, choices=MilestoneCategory.choices)
	description = models.CharField(max_length=500)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["created_at"]


class Participant(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	retrospective = models.ForeignKey(Retrospective, on_delete=models.CASCADE, related_name="participants")
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="participations")
	votes_remaining = models.IntegerField(default=3)
	joined_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=("retrospective", "user"), name="unique_retrospective_participant"),
		]
		ordering = ["joined_at"]


class AccessLog(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	retrospective = models.ForeignKey(Retrospective, on_delete=models.CASCADE, related_name="access_logs")
	action = models.CharField(max_length=32, choices=AccessLogAction.choices)
	triggered_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		related_name="triggered_access_logs",
		blank=True,
		null=True,
	)
	participant = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		related_name="participant_access_logs",
		blank=True,
		null=True,
	)
	timestamp = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-timestamp"]

# Create your models here.
