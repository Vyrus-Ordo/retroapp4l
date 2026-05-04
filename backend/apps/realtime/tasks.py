from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer


@shared_task
def timer_sync_task(retrospective_id: str):
    """
    Broadcasts timer.sync every 5 seconds while the timer is running.
    Self-reschedules via apply_async(countdown=5) until expired or paused.
    """
    from django.utils import timezone

    from apps.retrospectives.models import Retrospective, RetrospectiveStatus

    try:
        retro = Retrospective.objects.get(id=retrospective_id)
    except Retrospective.DoesNotExist:
        return

    # Stop if session closed or timer not started
    if retro.status == RetrospectiveStatus.CLOSED:
        return
    if not retro.timer_started_at or not retro.timer_duration_seconds:
        return
    # Stop if paused (will be restarted on resume)
    if retro.timer_paused_at:
        return

    elapsed = max(0, int((timezone.now() - retro.timer_started_at).total_seconds()))
    remaining = max(0, retro.timer_duration_seconds - elapsed)

    channel_layer = get_channel_layer()
    group_name = f"retro_{retrospective_id}"

    if remaining <= 0:
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "timer.expired",
                "phase": retro.status,
            },
        )
        return

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "timer.sync",
            "seconds_remaining": remaining,
        },
    )
    # Self-reschedule
    timer_sync_task.apply_async(args=[retrospective_id], countdown=5)
