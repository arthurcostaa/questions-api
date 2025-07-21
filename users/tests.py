from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from users.models import CustomUser


class CustomUserViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email='test@test.com', name='user test', password='Str0ngP4ssw0d#123'
        )

    def test_create_user(self):
        response = self.client.post(
            reverse('create'),
            data={
                'name': 'John Doe',
                'email': 'johndoe@email.com',
                'password': 'Str0ngP4ssw0d#123',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.json()['id'])
        self.assertEqual(response.json()['name'], 'John Doe')
        self.assertEqual(response.json()['email'], 'johndoe@email.com')
        self.assertIsNotNone(response.json()['date_joined'])

    def test_delete_user(self):
        response = self.client.delete(
            reverse('retrieve-update-destroy', kwargs={'pk': self.user.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_get_user(self):
        response = self.client.get(
            reverse('retrieve-update-destroy', kwargs={'pk': self.user.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.user.pk)
        self.assertEqual(response.json()['name'], self.user.name)
        self.assertEqual(response.json()['email'], self.user.email)
        self.assertIsNotNone(response.json()['date_joined'])
