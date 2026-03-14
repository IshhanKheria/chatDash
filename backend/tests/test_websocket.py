from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
import json

from config.asgi import application

User = get_user_model()


class WebSocketAuthTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='wsuser', email='ws@test.com', password='WsPass123'
        )
        self.token = str(AccessToken.for_user(self.user))

    async def test_connect_with_valid_token(self):
        communicator = WebsocketCommunicator(
            application, f'/ws/chat/?token={self.token}'
        )
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'connected')
        self.assertTrue(response['success'])
        await communicator.disconnect()

    async def test_connect_without_token(self):
        communicator = WebsocketCommunicator(application, '/ws/chat/')
        connected, subprotocol = await communicator.connect()
        self.assertFalse(connected)

    async def test_send_and_receive_message(self):
        user2 = User.objects.create_user(
            username='wsuser2', email='ws2@test.com', password='WsPass123'
        )
        token2 = str(AccessToken.for_user(user2))

        comm1 = WebsocketCommunicator(application, f'/ws/chat/?token={self.token}')
        comm2 = WebsocketCommunicator(application, f'/ws/chat/?token={token2}')

        await comm1.connect()
        await comm2.connect()
        await comm1.receive_json_from()  # connected message
        await comm2.receive_json_from()  # connected message

        await comm1.send_json_to({
            'type': 'send_message',
            'receiver_id': user2.id,
            'content': 'Hello via WebSocket!',
        })

        ack = await comm1.receive_json_from()
        self.assertEqual(ack['type'], 'message_sent')

        received = await comm2.receive_json_from()
        self.assertEqual(received['type'], 'receive_message')
        self.assertEqual(received['message']['content'], 'Hello via WebSocket!')

        await comm1.disconnect()
        await comm2.disconnect()
