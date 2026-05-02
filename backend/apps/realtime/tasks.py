from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer


@shared_task
def timer_sync_task(retrospective_id, seconds_remaining):
    channel_layer = get_channel_layer()
    group_name = f"retro_{retrospective_id}"
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "timer.sync",
            "seconds_remaining": seconds_remaining,
        }
    )
