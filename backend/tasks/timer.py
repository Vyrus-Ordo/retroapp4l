from celery import shared_task


@shared_task
def sync_timer(retrospective_id: str):
    return {"retrospective_id": retrospective_id, "status": "scheduled"}