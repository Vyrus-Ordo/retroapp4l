from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer


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
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json({
            "type": "session.snapshot",
            "phase": "lobby",
            "timer": None,
            "cards": [],
            "votes": [],
            "milestones": [],
            "participants": [],
            "action_items": []
        })
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "participant.joined",
                "user_id": str(user.id),
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
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "phase.changed",
                    "phase": content.get("phase"),
                    "timer_duration_seconds": content.get("timer_duration_seconds", 0)
                }
            )
        elif event_type == "milestone.presentation.start":
            # Facilitator starts presentation phase
            from apps.retrospectives.models import Milestone
            milestones = await database_sync_to_async(lambda: list(Milestone.objects.filter(retrospective_id=self.retrospective_id).order_by("created_at")))()
            if not milestones:
                # No milestones, skip phase
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
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "phase.changed", "phase": "check", "timer_duration_seconds": 0}
            )
        elif event_type == "timer.paused":

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "timer.paused",
                    "seconds_remaining": content.get("seconds_remaining", 0)
                }
            )
        elif event_type == "timer.resumed":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "timer.resumed",
                    "seconds_remaining": content.get("seconds_remaining", 0)
                }
            )
        elif event_type == "timer.sync":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "timer.sync",
                    "seconds_remaining": content.get("seconds_remaining", 0)
                }
            )
        elif event_type == "participant.joined":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "participant.joined",
                    "user_id": content.get("user_id"),
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

    async def participant_joined(self, event):
        if event.get("exclude_channel_name") == self.channel_name:
            return
        await self.send_json({"type": "participant.joined", "user_id": event["user_id"], "name": event["name"], "avatar_url": event["avatar_url"]})

    async def participant_joined_late(self, event):
        await self.send_json({"type": "participant.joined_late", "user_id": event["user_id"], "name": event["name"], "avatar_url": event["avatar_url"]})

    async def participant_left(self, event):
        await self.send_json({"type": "participant.left", "user_id": event["user_id"]})

    async def card_create(self, event):
        await self.send_json({"type": "card.created", "card": event["card"]})

    async def card_update(self, event):
        await self.send_json(
            {
                "type": "card.updated",
                "card_id": event["card_id"],
                "content": event["content"],
            }
        )

    async def card_delete(self, event):
        await self.send_json({"type": "card.deleted", "card_id": event["card_id"]})

    async def card_grouped(self, event):
        await self.send_json({"type": "card.grouped", "card_id": event["card_id"], "group_id": event["group_id"]})

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
                "author": event["author"],
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
