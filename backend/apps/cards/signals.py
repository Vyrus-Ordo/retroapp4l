from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.cards.models import Card
from apps.cards.serializers import CardSerializer


@receiver(post_save, sender=Card)
def card_saved(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    group = f"retro_{instance.retrospective_id}"
    card_data = CardSerializer(instance).data
    for field in ("id", "retrospective", "author", "group"):
        if card_data.get(field) is not None:
            card_data[field] = str(card_data[field])

    payload = {"card": card_data}
    if not created:
        payload = {"card_id": str(instance.id), "content": instance.content}

    async_to_sync(channel_layer.group_send)(
        group,
        {"type": "card_create" if created else "card_update", **payload}
    )

@receiver(post_delete, sender=Card)
def card_deleted(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    group = f"retro_{instance.retrospective_id}"
    async_to_sync(channel_layer.group_send)(
        group,
        {"type": "card_delete", "card_id": str(instance.id)}
    )
