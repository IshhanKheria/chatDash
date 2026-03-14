import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Message, Room, RoomMember

User = get_user_model()
logger = logging.getLogger(__name__)

# Track connected users: {user_id: channel_name}
connected_users = {}


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        self.user = user
        self.user_group = f'user_{user.id}'

        # Join user's personal channel group
        await self.channel_layer.group_add(self.user_group, self.channel_name)

        # Track connection
        connected_users[user.id] = self.channel_name

        # Join all user's rooms
        room_ids = await self.get_user_room_ids()
        for room_id in room_ids:
            await self.channel_layer.group_add(f'room_{room_id}', self.channel_name)

        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'success': True,
            'message': 'Connected to chat server.',
            'user_id': user.id,
        }))
        logger.info(f'User {user.id} connected via WebSocket.')

    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user.is_authenticated:
            connected_users.pop(self.user.id, None)
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
            logger.info(f'User {self.user.id} disconnected.')

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON.')
            return

        event_type = data.get('type')

        if event_type == 'send_message':
            await self.handle_send_message(data)
        elif event_type == 'send_room_message':
            await self.handle_send_room_message(data)
        elif event_type == 'edit_message':
            await self.handle_edit_message(data)
        elif event_type == 'delete_message':
            await self.handle_delete_message(data)
        elif event_type == 'typing':
            await self.handle_typing(data)
        else:
            await self.send_error(f'Unknown event type: {event_type}')

    # ---- Direct Message ----

    async def handle_send_message(self, data):
        receiver_id = data.get('receiver_id')
        content = data.get('content', '').strip()

        if not receiver_id:
            await self.send_error('receiver_id is required.')
            return
        if not content or len(content) > 5000:
            await self.send_error('content must be 1-5000 characters.')
            return

        receiver = await self.get_user(receiver_id)
        if not receiver:
            await self.send_error('Receiver not found.')
            return

        message = await self.save_message(
            sender=self.user, receiver=receiver, content=content
        )

        msg_dict = message.to_dict()

        # ACK to sender
        await self.send(text_data=json.dumps({
            'type': 'message_sent',
            'success': True,
            'message': msg_dict,
        }))

        # Deliver to receiver if online
        if receiver_id in connected_users:
            await self.channel_layer.group_send(
                f'user_{receiver_id}',
                {'type': 'chat_message', 'message': msg_dict}
            )

    # ---- Room Message ----

    async def handle_send_room_message(self, data):
        room_id = data.get('room_id')
        content = data.get('content', '').strip()

        if not room_id:
            await self.send_error('room_id is required.')
            return
        if not content or len(content) > 5000:
            await self.send_error('content must be 1-5000 characters.')
            return

        is_member = await self.is_room_member(room_id)
        if not is_member:
            await self.send_error('You are not a member of this room.')
            return

        message = await self.save_room_message(room_id=room_id, content=content)
        msg_dict = message.to_dict()

        # ACK to sender
        await self.send(text_data=json.dumps({
            'type': 'room_message_sent',
            'success': True,
            'message': msg_dict,
        }))

        # Broadcast to room (excluding sender)
        await self.channel_layer.group_send(
            f'room_{room_id}',
            {'type': 'room_message', 'message': msg_dict, 'sender_channel': self.channel_name}
        )

    # ---- Edit Message ----

    async def handle_edit_message(self, data):
        message_id = data.get('message_id')
        content = data.get('content', '').strip()

        if not message_id or not content:
            await self.send_error('message_id and content are required.')
            return

        message = await self.get_message(message_id)
        if not message:
            await self.send_error('Message not found.')
            return
        if message.sender_id != self.user.id:
            await self.send_error('You can only edit your own messages.')
            return
        if message.is_deleted:
            await self.send_error('Cannot edit a deleted message.')
            return

        message = await self.do_edit_message(message, content)
        msg_dict = message.to_dict()

        await self.send(text_data=json.dumps({
            'type': 'message_edited',
            'success': True,
            'message': msg_dict,
        }))

        # Notify other party
        if message.receiver_id and message.receiver_id in connected_users:
            await self.channel_layer.group_send(
                f'user_{message.receiver_id}',
                {'type': 'message_edited_event', 'message': msg_dict}
            )
        elif message.room_id:
            await self.channel_layer.group_send(
                f'room_{message.room_id}',
                {'type': 'message_edited_event', 'message': msg_dict, 'sender_channel': self.channel_name}
            )

    # ---- Delete Message ----

    async def handle_delete_message(self, data):
        message_id = data.get('message_id')
        if not message_id:
            await self.send_error('message_id is required.')
            return

        message = await self.get_message(message_id)
        if not message:
            await self.send_error('Message not found.')
            return
        if message.sender_id != self.user.id:
            await self.send_error('You can only delete your own messages.')
            return
        if message.is_deleted:
            await self.send_error('Message already deleted.')
            return

        message = await self.do_delete_message(message)
        msg_dict = message.to_dict()

        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'success': True,
            'message': msg_dict,
        }))

        if message.receiver_id and message.receiver_id in connected_users:
            await self.channel_layer.group_send(
                f'user_{message.receiver_id}',
                {'type': 'message_deleted_event', 'message': msg_dict}
            )
        elif message.room_id:
            await self.channel_layer.group_send(
                f'room_{message.room_id}',
                {'type': 'message_deleted_event', 'message': msg_dict, 'sender_channel': self.channel_name}
            )

    # ---- Typing Indicator ----

    async def handle_typing(self, data):
        receiver_id = data.get('receiver_id')
        room_id = data.get('room_id')
        is_typing = data.get('is_typing', False)

        typing_data = {
            'type': 'typing_indicator',
            'user_id': self.user.id,
            'username': self.user.username,
            'is_typing': is_typing,
        }

        if receiver_id and receiver_id in connected_users:
            await self.channel_layer.group_send(
                f'user_{receiver_id}',
                {'type': 'typing_event', **typing_data}
            )
        elif room_id:
            await self.channel_layer.group_send(
                f'room_{room_id}',
                {'type': 'typing_event', 'sender_channel': self.channel_name, **typing_data}
            )

    # ---- Channel Layer Handlers ----

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'receive_message',
            'success': True,
            'message': event['message'],
        }))

    async def room_message(self, event):
        if event.get('sender_channel') != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'receive_room_message',
                'success': True,
                'message': event['message'],
            }))

    async def message_edited_event(self, event):
        if event.get('sender_channel') != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'message_edited',
                'success': True,
                'message': event['message'],
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'message_edited',
                'success': True,
                'message': event['message'],
            }))

    async def message_deleted_event(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'success': True,
            'message': event['message'],
        }))

    async def typing_event(self, event):
        if event.get('sender_channel') != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing'],
            }))

    # ---- DB helpers ----

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_message(self, message_id):
        try:
            return Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, sender, receiver, content):
        return Message.objects.create(sender=sender, receiver=receiver, content=content)

    @database_sync_to_async
    def save_room_message(self, room_id, content):
        return Message.objects.create(sender=self.user, room_id=room_id, content=content)

    @database_sync_to_async
    def do_edit_message(self, message, content):
        message.content = content
        message.is_edited = True
        message.edited_at = timezone.now()
        message.save()
        return message

    @database_sync_to_async
    def do_delete_message(self, message):
        message.is_deleted = True
        message.deleted_at = timezone.now()
        message.save()
        return message

    @database_sync_to_async
    def is_room_member(self, room_id):
        return RoomMember.objects.filter(room_id=room_id, user=self.user).exists()

    @database_sync_to_async
    def get_user_room_ids(self):
        return list(RoomMember.objects.filter(user=self.user).values_list('room_id', flat=True))

    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'success': False,
            'message': message,
        }))
