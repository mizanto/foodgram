from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()


class UserViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user1 = User.objects.create_user(
            email='user1@user.co',
            username='user1',
            password='1qa!QA1qa'
        )
        cls.test_user2 = User.objects.create_user(
            email='user2@user.co',
            username='user2',
            password='1qa!QA1qa'
        )
        cls.test_token = Token.objects.create(user=cls.test_user1)

    def setUp(self):
        self.authorized_client = APIClient()
        self.authorized_client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.test_token.key)

        self.unauthorized_client = APIClient()

        self.test_user1.follower.create(
            author=self.test_user2, user=self.test_user1)

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
            reverse('api:users:user-detail', args=[self.test_user1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_me(self):
        response = self.authorized_client.get(reverse('api:users:user-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login(self):
        response = self.unauthorized_client.post(
            reverse('api:users:user-login'),
            {'email': 'user1@user.co', 'password': '1qa!QA1qa'}
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
                'email': 'new_user@user.co',
                'username': 'new_user',
                'password': '1qa!QA1qa'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_subscriptions(self):
        response = self.authorized_client.get(
            reverse('api:users:user-subscriptions'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], self.test_user2.email)

    def test_create_subscription(self):
        new_user = User.objects.create_user(
            email="user3@test.com", username='user3', password="password")
        response = self.authorized_client.post(
            reverse('api:users:user-subscribe', kwargs={'pk': new_user.id}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            self.test_user1.follower.filter(author=new_user).exists())

    def test_user_unsubscribe(self):
        new_user = User.objects.create_user(
            email="user3@test.com", username='user3', password="password")
        self.test_user1.follower.create(author=new_user, user=self.test_user1)
        response = self.authorized_client.delete(
            reverse('api:users:user-unsubscribe', kwargs={'pk': new_user.id}))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            self.test_user1.follower.filter(author=new_user).exists())
