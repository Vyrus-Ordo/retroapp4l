from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer


@database_sync_to_async
def persist_phase_advance(retrospective_id, user_id, target_phase):
    from apps.retrospectives.models import Retrospective, RetrospectiveStatus

    valid_statuses = {v for v in RetrospectiveStatus.values}
    if target_phase not in valid_statuses:
        return False
    try:
        retro = Retrospective.objects.get(id=retrospective_id)
        if str(retro.facilitator_id) != str(user_id):
            return False
        retro.status = target_phase
        retro.save(update_fields=["status"])
        return True
    except Retrospective.DoesNotExist:
        return False


@database_sync_to_async
def get_session_action_items(retrospective_id):
    from apps.actions.models import ActionItem
    from apps.actions.serializers import ActionItemSerializer

    items = ActionItem.objects.filter(retrospective_id=retrospective_id).select_related("assignee", "retrospective", "card")
    data = ActionItemSerializer(items, many=True).data
    return [
        {k: (str(v) if v is not None and not isinstance(v, (str, bool, int, float, list, dict)) else v) for k, v in item.items()}
        for item in data
    ]


@database_sync_to_async
def get_participant_id(retrospective_id, user_id):
    from apps.retrospectives.models import Participant

    return Participant.objects.filter(
        retrospective_id=retrospective_id,
        user_id=user_id,
    ).values_list("id", flat=True).first()


TIMED_PHASES = {"presentation", "check", "board", "grouping", "voting", "discussion", "actions"}

DEFAULT_PHASE_DURATIONS = {
    "presentation": 600,
    "check": 300,
    "board": 900,
    "grouping": 300,
    "voting": 180,
    "discussion": 900,
    "actions": 600,
}


@database_sync_to_async
def start_phase_timer(retrospective_id, phase):
    """Start timer for a timed phase. Returns duration in seconds, or 0 if not timed."""
    from django.utils import timezone

    from apps.retrospectives.models import Retrospective

    if phase not in TIMED_PHASES:
        return 0
    try:
        retro = Retrospective.objects.get(id=retrospective_id)
        duration = (retro.phase_durations or {}).get(phase) or DEFAULT_PHASE_DURATIONS.get(phase, 0)
        if duration <= 0:
            return 0
        retro.timer_started_at = timezone.now()
        retro.timer_paused_at = None
        retro.timer_duration_seconds = duration
        retro.save(update_fields=["timer_started_at", "timer_paused_at", "timer_duration_seconds"])
        return duration
    except Retrospective.DoesNotExist:
        return 0


@database_sync_to_async
def pause_timer(retrospective_id, user_id):
    """Pause the timer. Returns seconds_remaining if authorised, else None."""
    from django.utils import timezone

    from apps.retrospectives.models import Retrospective

    try:
        retro = Retrospective.objects.get(id=retrospective_id)
        if str(retro.facilitator_id) != str(user_id):
            return None
        if not retro.timer_started_at or retro.timer_paused_at:
            return None
        elapsed = max(0, int((timezone.now() - retro.timer_started_at).total_seconds()))
        remaining = max(0, (retro.timer_duration_seconds or 0) - elapsed)
        retro.timer_paused_at = timezone.now()
        retro.save(update_fields=["timer_paused_at"])
        return remaining
    except Retrospective.DoesNotExist:
        return None


@database_sync_to_async
def resume_timer(retrospective_id, user_id):
    """Resume the timer. Returns seconds_remaining if authorised, else None."""
    from django.utils import timezone

    from apps.retrospectives.models import Retrospective

    try:
        retro = Retrospective.objects.get(id=retrospective_id)
        if str(retro.facilitator_id) != str(user_id):
            return None
        if not retro.timer_paused_at or not retro.timer_started_at:
            return None
        elapsed_before_pause = max(0, int((retro.timer_paused_at - retro.timer_started_at).total_seconds()))
        remaining = max(0, (retro.timer_duration_seconds or 0) - elapsed_before_pause)
        # Reset started_at so elapsed resumes from correct point
        retro.timer_started_at = timezone.now() - (
            timezone.timedelta(seconds=(retro.timer_duration_seconds or 0) - remaining)
        )
        retro.timer_paused_at = None
        retro.save(update_fields=["timer_started_at", "timer_paused_at"])
        return remaining
    except Retrospective.DoesNotExist:
        return None


@database_sync_to_async
def get_connection_context(retrospective_id, user_id):
    from apps.retrospectives.models import Participant, Retrospective, RetrospectiveStatus

    try:
        retrospective = Retrospective.objects.only("facilitator_id", "status").get(id=retrospective_id)
    except Retrospective.DoesNotExist:
        return None

    has_access = retrospective.facilitator_id == user_id or Participant.objects.filter(
        retrospective_id=retrospective_id,
        user_id=user_id,
    ).exists()

    return {
        "has_access": has_access,
        "is_closed": retrospective.status == RetrospectiveStatus.CLOSED,
        "phase": retrospective.status,
    }


class RetrospectiveConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        url_route = self.scope.get("url_route") or {}
        route_kwargs = url_route.get("kwargs") or {}
        retrospective_id = route_kwargs.get("retrospective_id")
        if retrospective_id is None:
            await self.close(code=4000)
            return

        self.retrospective_id = retrospective_id
        self.group_name = f"retro_{self.retrospective_id}"
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return
        connection_context = await get_connection_context(self.retrospective_id, user.id)
        if connection_context is None:
            await self.close(code=4004)
            return
        if not connection_context["has_access"] or connection_context["is_closed"]:
            await self.close(code=4003)
            return
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        action_items = await get_session_action_items(self.retrospective_id)
        await self.send_json({
            "type": "session.snapshot",
            "phase": connection_context["phase"],
            "timer": None,
            "cards": [],
            "votes": [],
            "milestones": [],
            "participants": [],
            "action_items": action_items
        })
        participant_id = await get_participant_id(self.retrospective_id, user.id)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "participant.joined",
                "user_id": str(user.id),
                "participant_id": str(participant_id) if participant_id else None,
                "name": user.name,
                "avatar_url": user.avatar_url,
                "exclude_channel_name": self.channel_name,
            },
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        user_id = getattr(self.scope.get("user"), "id", None)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "participant.left",
                "user_id": str(user_id) if user_id is not None else None,
            }
        )

    # Presentation phase state (in-memory, per-process; for demo/prototype only)
    presentation_indices = {}

    async def receive_json(self, content, **kwargs):
        event_type = content.get("type")
        if event_type == "phase.advance":
            target_phase = content.get("phase")
            user = self.scope.get("user")
            persisted = await persist_phase_advance(self.retrospective_id, user.id, target_phase)
            if persisted:
                from apps.realtime.tasks import timer_sync_task
                duration = await start_phase_timer(self.retrospective_id, target_phase)
                if duration > 0:
                    timer_sync_task.apply_async(args=[str(self.retrospective_id)], countdown=5)
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "phase.changed",
                        "phase": target_phase,
                        "timer_duration_seconds": duration,
                    }
                )
        elif event_type == "milestone.presentation.start":
            # Facilitator starts presentation phase
            from apps.retrospectives.models import Milestone
            milestones = await database_sync_to_async(lambda: list(Milestone.objects.filter(retrospective_id=self.retrospective_id).order_by("created_at")))()
            if not milestones:
                # No milestones, skip phase
                user = self.scope.get("user")
                await persist_phase_advance(self.retrospective_id, user.id, "check")
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "phase.changed", "phase": "check", "timer_duration_seconds": 0}
                )
                return
            RetrospectiveConsumer.presentation_indices[self.retrospective_id] = 0
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "milestone.presentation", "index": 0, "total": len(milestones), "milestone": str(milestones[0].id)}
            )
        elif event_type == "milestone.presentation.next":
            from apps.retrospectives.models import Milestone
            milestones = await database_sync_to_async(lambda: list(Milestone.objects.filter(retrospective_id=self.retrospective_id).order_by("created_at")))()
            idx = RetrospectiveConsumer.presentation_indices.get(self.retrospective_id, 0)
            if idx < len(milestones) - 1:
                idx += 1
                RetrospectiveConsumer.presentation_indices[self.retrospective_id] = idx
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "milestone.presentation", "index": idx, "total": len(milestones), "milestone": str(milestones[idx].id)}
                )
        elif event_type == "milestone.presentation.prev":
            from apps.retrospectives.models import Milestone
            milestones = await database_sync_to_async(lambda: list(Milestone.objects.filter(retrospective_id=self.retrospective_id).order_by("created_at")))()
            idx = RetrospectiveConsumer.presentation_indices.get(self.retrospective_id, 0)
            if idx > 0:
                idx -= 1
                RetrospectiveConsumer.presentation_indices[self.retrospective_id] = idx
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "milestone.presentation", "index": idx, "total": len(milestones), "milestone": str(milestones[idx].id)}
                )
        elif event_type == "milestone.presentation.end":
            # Facilitator ends presentation phase
            user = self.scope.get("user")
            await persist_phase_advance(self.retrospective_id, user.id, "check")
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "phase.changed", "phase": "check", "timer_duration_seconds": 0}
            )
        elif event_type == "timer.pause":
            user = self.scope.get("user")
            remaining = await pause_timer(self.retrospective_id, user.id)
            if remaining is not None:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "timer.paused",
                        "seconds_remaining": remaining,
                    }
                )
        elif event_type == "timer.resume":
            user = self.scope.get("user")
            remaining = await resume_timer(self.retrospective_id, user.id)
            if remaining is not None:
                from apps.realtime.tasks import timer_sync_task
                timer_sync_task.apply_async(args=[str(self.retrospective_id)], countdown=5)
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "timer.resumed",
                        "seconds_remaining": remaining,
                    }
                )
        elif event_type == "participant.joined":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "participant.joined",
                    "user_id": content.get("user_id"),
                    "participant_id": content.get("participant_id"),
                    "name": content.get("name"),
                    "avatar_url": content.get("avatar_url")
                }
            )
        elif event_type == "participant.joined_late":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "participant.joined_late",
                    "user_id": content.get("user_id"),
                    "participant_id": content.get("participant_id"),
                    "name": content.get("name"),
                    "avatar_url": content.get("avatar_url")
                }
            )
        elif event_type == "card.create":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "card.create",
                    "card": content.get("card")
                }
            )
        elif event_type == "vote.cast":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "vote.cast",
                    "vote": content.get("vote")
                }
            )
        else:
            await self.send_json({"type": "ack", "data": content})

    async def phase_changed(self, event):
        await self.send_json({"type": "phase.changed", "phase": event["phase"], "timer_duration_seconds": event["timer_duration_seconds"]})

    async def milestone_presentation(self, event):
        # Broadcast current milestone index and id
        await self.send_json({
            "type": "milestone.presentation",
            "index": event["index"],
            "total": event["total"],
            "milestone": event["milestone"]
        })

    async def timer_paused(self, event):
        await self.send_json({"type": "timer.paused", "seconds_remaining": event["seconds_remaining"]})

    async def timer_resumed(self, event):
        await self.send_json({"type": "timer.resumed", "seconds_remaining": event["seconds_remaining"]})

    async def timer_sync(self, event):
        await self.send_json({"type": "timer.sync", "seconds_remaining": event["seconds_remaining"]})

    async def timer_expired(self, event):
        await self.send_json({"type": "timer.expired", "phase": event["phase"]})

    async def participant_joined(self, event):
        if event.get("exclude_channel_name") == self.channel_name:
            return
        await self.send_json({"type": "participant.joined", "user_id": event["user_id"], "participant_id": event.get("participant_id"), "name": event["name"], "avatar_url": event["avatar_url"]})

    async def participant_joined_late(self, event):
        await self.send_json({"type": "participant.joined_late", "user_id": event["user_id"], "participant_id": event.get("participant_id"), "name": event["name"], "avatar_url": event["avatar_url"]})

    async def participant_left(self, event):
        await self.send_json({"type": "participant.left", "user_id": event["user_id"]})

    async def card_create(self, event):
        card = dict(event["card"])
        user_id = getattr(self.scope.get("user"), "id", None)
        card["can_edit"] = str(user_id) == str(event.get("author_id"))
        await self.send_json({"type": "card.created", "card": card})

    async def card_update(self, event):
        card = event.get("card")
        if card is not None:
            card = dict(card)
            user_id = getattr(self.scope.get("user"), "id", None)
            card["can_edit"] = str(user_id) == str(event.get("author_id"))
        await self.send_json(
            {
                "type": "card.updated",
                "card_id": event["card_id"],
                "content": event["content"],
                "card": card,
            }
        )

    async def card_delete(self, event):
        await self.send_json({"type": "card.deleted", "card_id": event["card_id"]})

    async def card_grouped(self, event):
        await self.send_json(
            {
                "type": "card.grouped",
                "card_id": event["card_id"],
                "group_id": event["group_id"],
                "group_parent_id": event["group_id"],
            }
        )

    async def card_ungrouped(self, event):
        await self.send_json(
            {
                "type": "card.ungrouped",
                "card_id": event["card_id"],
                "previous_group_id": event["previous_group_id"],
            }
        )

    async def milestone_create(self, event):
        await self.send_json({"type": "milestone.create", "milestone": event["milestone"]})

    async def milestone_update(self, event):
        await self.send_json({"type": "milestone.update", "milestone": event["milestone"]})

    async def milestone_delete(self, event):
        await self.send_json({"type": "milestone.delete", "milestone_id": event["milestone_id"]})

    async def vote_cast(self, event):
        if "vote" in event:
            await self.send_json({"type": "vote.cast", "vote": event["vote"]})
            return

        await self.send_json(
            {
                "type": "vote.cast",
                "card_id": event["card_id"],
                "voter_id": event["voter_id"],
                "votes_remaining": event["votes_remaining"],
            }
        )

    async def vote_revoked(self, event):
        await self.send_json(
            {
                "type": "vote.revoked",
                "card_id": event["card_id"],
                "voter_id": event["voter_id"],
                "votes_remaining": event["votes_remaining"],
            }
        )

    async def action_created(self, event):
        await self.send_json({"type": "action.created", "action": event["action"]})

    async def action_updated(self, event):
        await self.send_json({"type": "action.updated", "action": event["action"]})

    async def action_deleted(self, event):
        await self.send_json({"type": "action.deleted", "action_id": event["action_id"]})

    async def action_check_updated(self, event):
        await self.send_json(
            {
                "type": "action.check_updated",
                "action_id": event["action_id"],
                "status": event["status"],
            }
        )

    async def discussion_focus_updated(self, event):
        await self.send_json(
            {
                "type": "discussion.focus_updated",
                "card_id": event["card_id"],
                "author": event.get("author"),
                "author_display": event.get("author_display"),
                "is_anonymous": event.get("is_anonymous", False),
                "column": event["column"],
                "content": event["content"],
                "vote_count": event["vote_count"],
            }
        )

    async def invite_status_updated(self, event):
        await self.send_json(
            {
                "type": "invite.status_updated",
                "invite_status": event["invite_status"],
                "expires_at": event.get("expires_at"),
            }
        )
