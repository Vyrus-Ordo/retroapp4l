from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.actions.models import ActionItem


def _serialize_action_item(instance):
    """Return a JSON-safe dict for broadcasting over WebSocket."""
    from apps.actions.serializers import ActionItemSerializer

    fresh = ActionItem.objects.select_related("assignee", "retrospective", "card").get(pk=instance.pk)
    data = ActionItemSerializer(fresh).data
    # Ensure all values are JSON-safe primitives (DRF already handles most, but be explicit)
    return {k: (str(v) if v is not None and not isinstance(v, (str, bool, int, float, list, dict)) else v) for k, v in data.items()}


@receiver(pre_save, sender=ActionItem)
def capture_previous_action_status(sender, instance, **kwargs):
    if not instance.pk:
        return

    previous = ActionItem.objects.filter(pk=instance.pk).values("status").first()
    if previous is None:
        return

    instance._previous_status = previous["status"]


@receiver(post_save, sender=ActionItem)
def broadcast_action_item_saved(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    group = f"retro_{instance.retrospective_id}"
    data = _serialize_action_item(instance)

    if created:
        async_to_sync(channel_layer.group_send)(
            group,
            {"type": "action_created", "action": data},
        )
    else:
        async_to_sync(channel_layer.group_send)(
            group,
            {"type": "action_updated", "action": data},
        )
        # Also notify clients that show the check phase (status change on previous retro items)
        previous_status = getattr(instance, "_previous_status", None)
        if previous_status is not None and previous_status != instance.status:
            async_to_sync(channel_layer.group_send)(
                group,
                {
                    "type": "action_check_updated",
                    "action_id": str(instance.id),
                    "status": instance.status,
                },
            )


@receiver(post_delete, sender=ActionItem)
def broadcast_action_item_deleted(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"retro_{instance.retrospective_id}",
        {"type": "action_deleted", "action_id": str(instance.id)},
    )