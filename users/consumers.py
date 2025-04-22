import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Message
from property.models import BookReq

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        self.request_id = self.scope['url_route']['kwargs']['request_id']
        self.room_group_name = f'chat_{self.request_id}'
        
        # Validate user has access to this chat
        can_access = await self.can_access_chat(self.request_id, self.scope["user"])
        if not can_access:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Notify others that user is online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user': self.scope["user"].username,
                'status': 'online'
            }
        )

    @database_sync_to_async
    def can_access_chat(self, request_id, user):
        try:
            book_request = BookReq.objects.get(id=request_id)
            return (user == book_request.booker) or (user == book_request.properid.owner)
        except BookReq.DoesNotExist:
            return False

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Notify others that user is offline
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user': self.scope["user"].username,
                    'status': 'offline'
                }
            )
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    @database_sync_to_async
    def save_message(self, content, sender_username):
        try:
            user = User.objects.get(username=sender_username)
            book_request = BookReq.objects.get(id=self.request_id)
            message = Message.objects.create(
                request=book_request,
                sender=user,
                content=content,
                timestamp=timezone.now(),
                is_read=False
            )
            print(f"Message saved: {message}")  # Debug log
            return message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"Error saving message: {e}")
            raise

    @database_sync_to_async
    def mark_messages_as_read(self, user):
        Message.objects.filter(
            request_id=self.request_id
        ).exclude(
            sender=user
        ).update(is_read=True)

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'chat_message')
            
            if message_type == 'chat_message':
                message_content = text_data_json['message']
                if not message_content.strip():
                    return
                
                # Save message first
                timestamp = await self.save_message(message_content, self.scope["user"].username)
                
                if timestamp:
                    # Send to all clients in the group, including sender
                    message_data = {
                        'type': 'chat_message',
                        'message': message_content,
                        'sender': self.scope["user"].username,
                        'timestamp': timestamp
                    }
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        message_data
                    )
                    print(f"Message broadcast to group: {self.room_group_name}")
        except Exception as e:
            print(f"Error in receive: {e}")

    async def chat_message(self, event):
        try:
            # Forward the message to WebSocket
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'message': event['message'],
                'sender': event['sender'],
                'timestamp': event['timestamp']
            }))
            print(f"Message sent to client: {event['sender']}")
        except Exception as e:
            print(f"Error in chat_message: {e}")

    async def typing_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'sender': event['sender']
        }))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user': event['user'],
            'status': event['status']
        }))
