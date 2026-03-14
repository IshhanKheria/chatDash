from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.chat.models import Message

User = get_user_model()


class MessageHistoryTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', email='user1@test.com', password='Pass123User')
        self.user2 = User.objects.create_user(username='user2', email='user2@test.com', password='Pass123User')
        login = self.client.post('/api/auth/login', {'email': 'user1@test.com', 'password': 'Pass123User'}, format='json')
        self.token = login.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        Message.objects.create(sender=self.user1, receiver=self.user2, content='Hello user2')
        Message.objects.create(sender=self.user2, receiver=self.user1, content='Hello user1')

    def test_get_message_history(self):
        response = self.client.get(f'/api/messages/history/{self.user2.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']['messages']), 2)

    def test_cannot_edit_others_message(self):
        msg = Message.objects.create(sender=self.user2, receiver=self.user1, content='Not yours')
        response = self.client.put(f'/api/messages/{msg.id}/', {'content': 'Hacked'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_own_message(self):
        msg = Message.objects.create(sender=self.user1, receiver=self.user2, content='Original')
        response = self.client.put(f'/api/messages/{msg.id}/', {'content': 'Edited'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        msg.refresh_from_db()
        self.assertTrue(msg.is_edited)

    def test_delete_own_message(self):
        msg = Message.objects.create(sender=self.user1, receiver=self.user2, content='To delete')
        response = self.client.delete(f'/api/messages/{msg.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        msg.refresh_from_db()
        self.assertTrue(msg.is_deleted)

    def test_unauthorized_history(self):
        client = APIClient()
        response = client.get(f'/api/messages/history/{self.user2.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
