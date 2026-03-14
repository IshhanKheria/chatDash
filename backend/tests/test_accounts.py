from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register'

    def test_successful_registration(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123',
            'password_confirm': 'TestPass123',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('tokens', response.data)

    def test_duplicate_email(self):
        User.objects.create_user(username='existing', email='test@example.com', password='Pass123!')
        data = {'username': 'new', 'email': 'test@example.com', 'password': 'TestPass123', 'password_confirm': 'TestPass123'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weak_password(self):
        data = {'username': 'user', 'email': 'a@b.com', 'password': 'weak', 'password_confirm': 'weak'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_username(self):
        data = {'username': 'u!', 'email': 'a@b.com', 'password': 'TestPass123', 'password_confirm': 'TestPass123'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='loginuser', email='login@example.com', password='LoginPass123'
        )

    def test_successful_login(self):
        response = self.client.post('/api/auth/login', {'email': 'login@example.com', 'password': 'LoginPass123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)

    def test_wrong_password(self):
        response = self.client.post('/api/auth/login', {'email': 'login@example.com', 'password': 'wrong'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_endpoint_authenticated(self):
        login_response = self.client.post('/api/auth/login', {'email': 'login@example.com', 'password': 'LoginPass123'}, format='json')
        token = login_response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/auth/me')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'login@example.com')

    def test_me_endpoint_unauthenticated(self):
        response = self.client.get('/api/auth/me')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
