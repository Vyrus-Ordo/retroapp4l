from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.cards.models import Card, CardVote
from apps.cards.serializers import CardSerializer
from apps.retrospectives.models import Participant


@receiver(pre_save, sender=Card)
def capture_card_previous_state(sender, instance, **kwargs):
    if not instance.pk:
        return

    previous_card = Card.objects.filter(pk=instance.pk).values("content", "group_id").first()
    if previous_card is None:
        return

    instance._previous_content = previous_card["content"]
    instance._previous_group_id = previous_card["group_id"]


@receiver(post_save, sender=Card)
def card_saved(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    group = f"retro_{instance.retrospective_id}"
    card_data = CardSerializer(instance).data
    for field in ("id", "retrospective", "author", "group"):
        if card_data.get(field) is not None:
            card_data[field] = str(card_data[field])

    if created:
        async_to_sync(channel_layer.group_send)(
            group,
            {"type": "card_create", "card": card_data}
        )
        return

    previous_content = getattr(instance, "_previous_content", None)
    previous_group_id = getattr(instance, "_previous_group_id", None)

    if previous_content != instance.content:
        async_to_sync(channel_layer.group_send)(
            group,
            {
                "type": "card_update",
                "card_id": str(instance.id),
                "content": instance.content,
            }
        )

    if previous_group_id != instance.group_id:
        if instance.group_id is None and previous_group_id is not None:
            async_to_sync(channel_layer.group_send)(
                group,
                {
                    "type": "card_ungrouped",
                    "card_id": str(instance.id),
                    "previous_group_id": str(previous_group_id),
                }
            )
        elif instance.group_id is not None:
            async_to_sync(channel_layer.group_send)(
                group,
                {
                    "type": "card_grouped",
                    "card_id": str(instance.id),
                    "group_id": str(instance.group_id),
                }
            )

@receiver(post_delete, sender=Card)
def card_deleted(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    group = f"retro_{instance.retrospective_id}"
    async_to_sync(channel_layer.group_send)(
        group,
        {"type": "card_delete", "card_id": str(instance.id)}
    )


@receiver(post_save, sender=CardVote)
def card_vote_saved(sender, instance, created, **kwargs):
    if not created:
        return

    participant = Participant.objects.get(retrospective=instance.card.retrospective, user=instance.voter)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"retro_{instance.card.retrospective_id}",
        {
            "type": "vote_cast",
            "card_id": str(instance.card_id),
            "voter_id": str(instance.voter_id),
            "votes_remaining": participant.votes_remaining,
        },
    )


@receiver(post_delete, sender=CardVote)
def card_vote_deleted(sender, instance, **kwargs):
    participant = Participant.objects.get(retrospective=instance.card.retrospective, user=instance.voter)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"retro_{instance.card.retrospective_id}",
        {
            "type": "vote_revoked",
            "card_id": str(instance.card_id),
            "voter_id": str(instance.voter_id),
            "votes_remaining": participant.votes_remaining,
        },
    )
