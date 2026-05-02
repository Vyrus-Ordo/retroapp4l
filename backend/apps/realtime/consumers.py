from channels.generic.websocket import AsyncJsonWebsocketConsumer


class RetrospectiveConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.retrospective_id = self.scope["url_route"]["kwargs"]["retrospective_id"]
        self.group_name = f"retrospective-{self.retrospective_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json({"type": "session.snapshot", "data": {"status": "connected"}})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        await self.send_json({"type": "ack", "data": content})