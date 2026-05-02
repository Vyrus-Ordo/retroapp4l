from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.retrospectives.models import Milestone
from apps.retrospectives.serializers import MilestoneSerializer


@receiver(post_save, sender=Milestone)
def milestone_saved(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    group = f"retro_{instance.retrospective_id}"
    milestone_data = MilestoneSerializer(instance).data
    async_to_sync(channel_layer.group_send)(
        group,
        {
            "type": "milestone_create" if created else "milestone_update",
            "milestone": milestone_data
        }
    )

@receiver(post_delete, sender=Milestone)
def milestone_deleted(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    group = f"retro_{instance.retrospective_id}"
    async_to_sync(channel_layer.group_send)(
        group,
        {
            "type": "milestone_delete",
            "milestone_id": str(instance.id)
        }
    )
