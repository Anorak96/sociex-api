import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat import models
from user.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id =f"chat_{self.scope['url_route']['kwargs']['room_id']}"
        await self.channel_layer.group_add(
            self.room_id, 
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_id, 
            self.channel_name
        )
        self.close(code)

    async def receive(self, text_data):
        data = json.loads(text_data)
        room_id = data["room_id"]
        body = data["body"]
        sender_user = data["sender"]

        event = {
            "type": "send_message",
            "chat": room_id,
            "id": room_id,
            "body": body,
            "sender": sender_user
        }
        await self.channel_layer.group_send(self.room_id, event)

    async def send_message(self, event):
        room_id = event["chat"]
        body = event["body"]
        sender_user = event["sender"]

        await self.create_chat(event)
        user_sender = await self.get_user(sender_user)

        response = {
            "id": room_id,
            "body": body,
            "sender": user_sender
        }
        await self.send(text_data=json.dumps(response))

    @database_sync_to_async
    def create_chat(self, data):
        try:
            print("Data", data)
            chat_ = models.Chat.objects.get(id=data['id'])
            sender_ = User.objects.get(username=data['sender'])
            models.ChatMessage.objects.create(chat=chat_, sender=sender_, body=data['body'])
        except (models.Chat.DoesNotExist, User.DoesNotExist):
            return None

    @database_sync_to_async
    def get_user(self, sender):
        try:
            user = User.objects.get(username=sender)
            return {
                "username": user.username
            }
        except User.DoesNotExist:
            return {"data": "Unknown"}