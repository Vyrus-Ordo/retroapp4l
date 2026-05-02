"""Celery tasks for invite link management."""

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.utils import timezone


@shared_task(name="tasks.invite.auto_block_invite")
def auto_block_invite(retrospective_id: str) -> None:
	"""Auto-block invite link after temporary reopen window expires."""
	from apps.retrospectives.models import AccessLog, AccessLogAction, Retrospective

	try:
		retrospective = Retrospective.objects.get(id=retrospective_id)
	except Retrospective.DoesNotExist:
		return

	now = timezone.now()

	# Only block if still temporarily open and the window has expired
	if (
		retrospective.invite_temporarily_open_until is None
		or retrospective.invite_temporarily_open_until > now
	):
		return

	retrospective.invite_temporarily_open_until = None
	retrospective.save(update_fields=["invite_temporarily_open_until"])

	AccessLog.objects.create(
		retrospective=retrospective,
		action=AccessLogAction.LINK_AUTO_BLOCKED,
	)

	channel_layer = get_channel_layer()
	async_to_sync(channel_layer.group_send)(
		f"retro_{retrospective.id}",
		{
			"type": "invite_status_updated",
			"invite_status": "blocked",
			"expires_at": None,
		},
	)
