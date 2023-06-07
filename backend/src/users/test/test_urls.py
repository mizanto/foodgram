from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()


class UserViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(
            email='user@user.co',
            username='user',
            password='1qa!QA1qa'
        )
        cls.test_token = Token.objects.create(user=cls.test_user)

    def setUp(self):
        self.authorized_client = APIClient()
        self.authorized_client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.test_token.key)

        self.unauthorized_client = APIClient()

    def test_user_list_authorized_user(self):
        response = self.authorized_client.get(
            reverse('api:users:user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_list_unauthorized_user(self):
        response = self.unauthorized_client.get(
            reverse('api:users:user-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_detail_unauthorized_user(self):
        response = self.unauthorized_client.get(
            reverse('api:users:user-detail', args=[self.test_user.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_me(self):
        response = self.authorized_client.get(reverse('api:users:user-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login(self):
        response = self.unauthorized_client.post(
            reverse('api:users:user-login'),
            {'email': 'user@user.co', 'password': '1qa!QA1qa'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_authorized_user(self):
        response = self.authorized_client.post(
            reverse('api:users:user-logout'))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_unauthorized_user(self):
        response = self.unauthorized_client.post(
            reverse('api:users:user-logout'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_authorized_user(self):
        response = self.authorized_client.post(
            reverse('api:users:user-set-password'),
            {'current_password': '1qa!QA1qa', 'new_password': '1qa!QA2qa'}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_change_password_unauthorized_user(self):
        response = self.unauthorized_client.post(
            reverse('api:users:user-set-password'),
            {'current_password': '1qa!QA1qa', 'new_password': '1qa!QA2qa'}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_registraion(self):
        response = self.unauthorized_client.post(
            reverse('api:users:user-list'),
            {
                'email': 'user2@user.co',
                'username': 'user2',
                'password': '1qa!QA1qa'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
