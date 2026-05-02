from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.actions.models import ActionItem


@receiver(pre_save, sender=ActionItem)
def capture_previous_action_status(sender, instance, **kwargs):
    if not instance.pk:
        return

    previous = ActionItem.objects.filter(pk=instance.pk).values("status").first()
    if previous is None:
        return

    instance._previous_status = previous["status"]


@receiver(post_save, sender=ActionItem)
def broadcast_action_status_update(sender, instance, created, **kwargs):
    if created:
        return

    previous_status = getattr(instance, "_previous_status", None)
    if previous_status == instance.status:
        return

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"retro_{instance.retrospective_id}",
        {
            "type": "action_check_updated",
            "action_id": str(instance.id),
            "status": instance.status,
        },
    )