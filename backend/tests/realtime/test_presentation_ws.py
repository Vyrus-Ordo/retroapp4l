import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

from apps.actions.models import ActionItem
from apps.cards.models import Card, CardVote
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
def close_retro(retro):
    retro.status = RetrospectiveStatus.CLOSED
    retro.save(update_fields=["status"])
    return retro

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


@database_sync_to_async
def group_card(child_card, parent_card):
    child_card.group = parent_card
    child_card.save(update_fields=["group"])


@database_sync_to_async
def ungroup_card(card):
    card.group = None
    card.save(update_fields=["group"])


@database_sync_to_async
def create_voting_retro(user):
    return Retrospective.objects.create(title="Sprint 4", team_key="vote-team", facilitator=user, status=RetrospectiveStatus.VOTING)


@database_sync_to_async
def cast_vote(retro, card, voter):
    participant = Participant.objects.get(retrospective=retro, user=voter)
    participant.votes_remaining -= 1
    participant.save(update_fields=["votes_remaining"])
    return CardVote.objects.create(card=card, voter=voter)


@database_sync_to_async
def revoke_vote(retro, vote, voter):
    participant = Participant.objects.get(retrospective=retro, user=voter)
    participant.votes_remaining += 1
    participant.save(update_fields=["votes_remaining"])
    vote.delete()


@database_sync_to_async
def update_action_status(action_item, status_value):
    action_item.status = status_value
    action_item.save(update_fields=["status"])


@database_sync_to_async
def create_discussion_retro(user):
    return Retrospective.objects.create(title="Sprint 5", team_key="discussion-team", facilitator=user, status=RetrospectiveStatus.DISCUSSION)

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
            "author_display": user.name,
            "column": "loved",
            "content": "Primeiro card",
            "is_anonymous": False,
            "group": None,
            "position": 0,
            "vote_count": 0,
            "can_edit": True,
            "created_at": created["card"]["created_at"],
        },
    }

    await update_card(card, "Card atualizado")
    updated = await communicator.receive_json_from()
    assert updated == {
        "type": "card.updated",
        "card_id": str(card.id),
        "content": "Card atualizado",
        "card": updated["card"],
    }
    assert updated["card"]["author"] == str(user.id)
    assert updated["card"]["author_name"] == user.name
    assert updated["card"]["can_edit"] is True

    card.is_anonymous = True
    await database_sync_to_async(card.save)(update_fields=["is_anonymous"])
    anonymized = await communicator.receive_json_from()
    assert anonymized["type"] == "card.updated"
    assert anonymized["card"]["id"] == str(card.id)
    assert anonymized["card"]["author"] is None
    assert anonymized["card"]["author_name"] is None
    assert anonymized["card"]["author_display"] == "Anonymous"
    assert anonymized["card"]["is_anonymous"] is True
    assert anonymized["card"]["can_edit"] is True

    card_id = str(card.id)
    await delete_card(card)
    deleted = await communicator.receive_json_from()
    assert deleted == {
        "type": "card.deleted",
        "card_id": card_id,
    }

    await communicator.disconnect()


@database_sync_to_async
def create_named_user(name, email):
    return User.objects.create_user(name=name, email=email, password="supersecret123")


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_participant_join_is_broadcast_to_other_connected_clients():
    facilitator = await create_named_user("Facilitator", "facilitator-join@example.com")
    joining_user = await create_named_user("Participant", "participant-join@example.com")
    retro = await create_retro(facilitator)
    await create_participant(retro, facilitator)
    await create_participant(retro, joining_user)

    facilitator_token = str(AccessToken.for_user(facilitator))
    joining_token = str(AccessToken.for_user(joining_user))

    facilitator_communicator = WebsocketCommunicator(
        application,
        f"/ws/retrospectives/{retro.id}/?token={facilitator_token}",
    )
    connected, _ = await facilitator_communicator.connect()
    assert connected

    snapshot = await facilitator_communicator.receive_json_from()
    assert snapshot["type"] == "session.snapshot"

    joining_communicator = WebsocketCommunicator(
        application,
        f"/ws/retrospectives/{retro.id}/?token={joining_token}",
    )
    connected, _ = await joining_communicator.connect()
    assert connected

    joining_snapshot = await joining_communicator.receive_json_from()
    assert joining_snapshot["type"] == "session.snapshot"

    joined_event = await facilitator_communicator.receive_json_from()
    assert joined_event == {
        "type": "participant.joined",
        "user_id": str(joining_user.id),
        "name": joining_user.name,
        "avatar_url": joining_user.avatar_url,
    }

    await facilitator_communicator.disconnect()
    await joining_communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_closed_retro_rejects_participant_websocket_connection():
    facilitator = await create_named_user("Facilitator", "facilitator-closed@example.com")
    participant = await create_named_user("Participant", "participant-closed@example.com")
    retro = await create_retro(facilitator)
    await create_participant(retro, facilitator)
    await create_participant(retro, participant)
    await close_retro(retro)

    participant_token = str(AccessToken.for_user(participant))
    communicator = WebsocketCommunicator(
        application,
        f"/ws/retrospectives/{retro.id}/?token={participant_token}",
    )

    connected, _ = await communicator.connect()

    assert not connected


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_card_grouping_events_are_broadcast():
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

    parent = await create_card(retro, user, "Pai")
    await communicator.receive_json_from()
    child = await create_card(retro, user, "Filho")
    await communicator.receive_json_from()

    await group_card(child, parent)
    grouped = await communicator.receive_json_from()
    assert grouped == {
        "type": "card.grouped",
        "card_id": str(child.id),
        "group_id": str(parent.id),
        "group_parent_id": str(parent.id),
    }

    await ungroup_card(child)
    ungrouped = await communicator.receive_json_from()
    assert ungrouped == {
        "type": "card.ungrouped",
        "card_id": str(child.id),
        "previous_group_id": str(parent.id),
    }

    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_vote_events_are_broadcast():
    author = await create_user()
    voter = await database_sync_to_async(User.objects.create_user)(name="Voter", email="voter-ws@example.com", password="supersecret123")
    retro = await create_voting_retro(author)
    await create_participant(retro, author)
    await create_participant(retro, voter)
    card = await database_sync_to_async(Card.objects.create)(retrospective=retro, author=author, column="loathed", content="Pain")

    token = str(AccessToken.for_user(voter))
    communicator = WebsocketCommunicator(
        application,
        f"/ws/retrospectives/{retro.id}/?token={token}",
    )
    connected, _ = await communicator.connect()
    assert connected

    snapshot = await communicator.receive_json_from()
    assert snapshot["type"] == "session.snapshot"

    vote = await cast_vote(retro, card, voter)
    cast_event = await communicator.receive_json_from()
    assert cast_event == {
        "type": "vote.cast",
        "card_id": str(card.id),
        "voter_id": str(voter.id),
        "votes_remaining": 2,
    }

    await revoke_vote(retro, vote, voter)
    revoked_event = await communicator.receive_json_from()
    assert revoked_event == {
        "type": "vote.revoked",
        "card_id": str(card.id),
        "voter_id": str(voter.id),
        "votes_remaining": 3,
    }

    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_action_check_update_is_broadcast():
    user = await create_user()
    retro = await create_retro(user)
    await create_participant(retro, user)
    action_item = await database_sync_to_async(ActionItem.objects.create)(retrospective=retro, description="Atualizar guia", assignee=user)

    token = str(AccessToken.for_user(user))
    communicator = WebsocketCommunicator(
        application,
        f"/ws/retrospectives/{retro.id}/?token={token}",
    )
    connected, _ = await communicator.connect()
    assert connected
    snapshot = await communicator.receive_json_from()
    assert snapshot["type"] == "session.snapshot"

    await update_action_status(action_item, "in_progress")
    event = await communicator.receive_json_from()
    assert event == {
        "type": "action.check_updated",
        "action_id": str(action_item.id),
        "status": "in_progress",
    }

    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_discussion_focus_update_is_broadcast():
    user = await create_user()
    retro = await create_discussion_retro(user)
    await create_participant(retro, user)
    card = await create_card(retro, user, "API instável")

    token = str(AccessToken.for_user(user))
    communicator = WebsocketCommunicator(
        application,
        f"/ws/retrospectives/{retro.id}/?token={token}",
    )
    connected, _ = await communicator.connect()
    assert connected
    snapshot = await communicator.receive_json_from()
    assert snapshot["type"] == "session.snapshot"

    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"retro_{retro.id}",
        {
            "type": "discussion_focus_updated",
            "card_id": str(card.id),
            "author": None,
            "author_display": "Anonymous",
            "is_anonymous": True,
            "column": card.column,
            "content": card.content,
            "vote_count": 0,
        },
    )

    event = await communicator.receive_json_from()
    assert event == {
        "type": "discussion.focus_updated",
        "card_id": str(card.id),
        "author": None,
        "author_display": "Anonymous",
        "is_anonymous": True,
        "column": card.column,
        "content": card.content,
        "vote_count": 0,
    }

    await communicator.disconnect()
