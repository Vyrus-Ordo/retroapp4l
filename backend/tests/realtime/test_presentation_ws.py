import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

from apps.cards.models import Card
from apps.retrospectives.models import Milestone, MilestoneCategory, Participant, Retrospective, RetrospectiveStatus
from config.asgi import application

User = get_user_model()

@database_sync_to_async
def create_user():
    return User.objects.create_user(name="Facilitator", email="facilitator-ws@example.com", password="supersecret123")

@database_sync_to_async
def create_retro(user):
    return Retrospective.objects.create(title="Sprint 3", team_key="ws-team", facilitator=user, status=RetrospectiveStatus.PRESENTATION)

@database_sync_to_async
def create_participant(retro, user):
    return Participant.objects.create(retrospective=retro, user=user, votes_remaining=3)

@database_sync_to_async
def create_milestone(retro, user, category, desc):
    return Milestone.objects.create(retrospective=retro, author=user, category=category, description=desc)


@database_sync_to_async
def create_card(retro, user, content):
    return Card.objects.create(retrospective=retro, author=user, column="loved", content=content)


@database_sync_to_async
def update_card(card, content):
    card.content = content
    card.save(update_fields=["content"])
    return card


@database_sync_to_async
def delete_card(card):
    card.delete()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_milestone_presentation_navigation():
    user = await create_user()
    retro = await create_retro(user)
    await create_participant(retro, user)
    m1 = await create_milestone(retro, user, MilestoneCategory.ACHIEVEMENT, "Primeiro")
    m2 = await create_milestone(retro, user, MilestoneCategory.CHALLENGE, "Segundo")

    token = str(AccessToken.for_user(user))
    communicator = WebsocketCommunicator(
        application,
        f"/ws/retrospectives/{retro.id}/?token={token}"
    )
    connected, _ = await communicator.connect()
    assert connected

    # Consome mensagem inicial de snapshot
    snapshot = await communicator.receive_json_from()
    assert snapshot["type"] == "session.snapshot"

    # Inicia apresentação
    await communicator.send_json_to({"type": "milestone.presentation.start"})
    response = await communicator.receive_json_from()
    assert response["type"] == "milestone.presentation"
    assert response["index"] == 0
    assert response["milestone"] == str(m1.id)

    # Avança para o próximo marco
    await communicator.send_json_to({"type": "milestone.presentation.next"})
    response = await communicator.receive_json_from()
    assert response["type"] == "milestone.presentation"
    assert response["index"] == 1
    assert response["milestone"] == str(m2.id)

    # Volta para o primeiro marco
    await communicator.send_json_to({"type": "milestone.presentation.prev"})
    response = await communicator.receive_json_from()
    assert response["type"] == "milestone.presentation"
    assert response["index"] == 0
    assert response["milestone"] == str(m1.id)

    # Encerra apresentação
    await communicator.send_json_to({"type": "milestone.presentation.end"})
    response = await communicator.receive_json_from()
    assert response["type"] == "phase.changed"
    assert response["phase"] == "check"

    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_card_events_are_broadcast():
    user = await create_user()
    retro = await create_retro(user)
    await create_participant(retro, user)

    token = str(AccessToken.for_user(user))
    communicator = WebsocketCommunicator(
        application,
        f"/ws/retrospectives/{retro.id}/?token={token}",
    )
    connected, _ = await communicator.connect()
    assert connected

    snapshot = await communicator.receive_json_from()
    assert snapshot["type"] == "session.snapshot"

    card = await create_card(retro, user, "Primeiro card")
    created = await communicator.receive_json_from()
    assert created == {
        "type": "card.created",
        "card": {
            "id": str(card.id),
            "retrospective": str(retro.id),
            "author": str(user.id),
            "author_name": user.name,
            "column": "loved",
            "content": "Primeiro card",
            "group": None,
            "position": 0,
            "created_at": created["card"]["created_at"],
        },
    }

    await update_card(card, "Card atualizado")
    updated = await communicator.receive_json_from()
    assert updated == {
        "type": "card.updated",
        "card_id": str(card.id),
        "content": "Card atualizado",
    }

    card_id = str(card.id)
    await delete_card(card)
    deleted = await communicator.receive_json_from()
    assert deleted == {
        "type": "card.deleted",
        "card_id": card_id,
    }

    await communicator.disconnect()
