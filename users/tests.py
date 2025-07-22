from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from users.models import CustomUser


class CustomUserCreateViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

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


class CustomUserRetrieveUpdateDestroyViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(
            email='test1@test.com', name='user test 1', password='Str0ngP4ssw0d#123'
        )
        self.user2 = CustomUser.objects.create_user(
            email='test2@test.com', name='user test 2', password='Str0ngP4ssw0d#123'
        )
        self.access_token = AccessToken.for_user(self.user1)

    def test_get_with_unauthenticated_user(self):
        response = self.client.get(
            reverse('retrieve-update-destroy', kwargs={'pk': self.user1.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertDictEqual(
            response.json(),
            {'detail': 'Authentication credentials were not provided.'}
        )

    def test_update_put_user_with_unauthenticated_user(self):
        response = self.client.put(
            reverse('retrieve-update-destroy', kwargs={'pk': self.user1.pk}),
            data={
                'email': 'test@test.com',
                'name': 'user test2',
                'password': 'Str0ngP4ssw0d#12345',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertDictEqual(
            response.json(),
            {'detail': 'Authentication credentials were not provided.'}
        )

    def test_update_patch_user_with_unauthenticated_user(self):
        response = self.client.patch(
            reverse('retrieve-update-destroy', kwargs={'pk': self.user1.pk}),
            data={'name': 'user test2'}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertDictEqual(
            response.json(),
            {'detail': 'Authentication credentials were not provided.'}
        )

    def test_delete_user_with_unauthenticated_user(self):
        response = self.client.delete(
            reverse('retrieve-update-destroy', kwargs={'pk': self.user1.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertDictEqual(
            response.json(),
            {'detail': 'Authentication credentials were not provided.'}
        )

    def test_get_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(
            reverse('retrieve-update-destroy', kwargs={'pk': self.user1.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.user1.pk)
        self.assertEqual(response.json()['name'], self.user1.name)
        self.assertEqual(response.json()['email'], self.user1.email)
        self.assertIsNotNone(response.json()['date_joined'])

    def test_delete_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.delete(
            reverse('retrieve-update-destroy', kwargs={'pk': self.user1.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user1.refresh_from_db()
        self.assertFalse(self.user1.is_active)

    def test_delete_another_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.delete(
            reverse('retrieve-update-destroy', kwargs={'pk': self.user2.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(
            response.json(),
            {'detail': 'You do not have permission to perform this action.'}
        )

    def test_delete_unexistent_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.delete(
            reverse('retrieve-update-destroy', kwargs={'pk': 99999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(
            response.json(),
            {'detail': 'No CustomUser matches the given query.'}
        )

    def test_update_put_user(self):
        data = {
            'email': 'test@test.com',
            'name': 'user test2',
            'password': 'Str0ngP4ssw0d#12345',
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.put(
            reverse('retrieve-update-destroy', kwargs={'pk': self.user1.pk}),
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.user1.pk)
        self.assertEqual(response.json()['name'], data['name'])
        self.assertEqual(response.json()['email'], data['email'])
        self.assertIsNotNone(response.json()['date_joined'])

    def test_update_put_another_user(self):
        data = {
            'email': 'test@test.com',
            'name': 'user test2',
            'password': 'Str0ngP4ssw0d#12345',
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.put(
            reverse('retrieve-update-destroy', kwargs={'pk': self.user2.pk}),
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(
            response.json(),
            {'detail': 'You do not have permission to perform this action.'}
        )

    def test_update_put_unexistent_user(self):
        data = {
            'email': 'test@test.com',
            'name': 'user test2',
            'password': 'Str0ngP4ssw0d#12345',
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.put(
            reverse('retrieve-update-destroy', kwargs={'pk': 99999}),
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(
            response.json(),
            {'detail': 'No CustomUser matches the given query.'}
        )

    def test_update_put_user_with_email_already_used(self):
        data = {
            'email': self.user2.email,
            'name': 'user test1',
            'password': 'Str0ngP4ssw0d#123',
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.put(
            reverse('retrieve-update-destroy', kwargs={'pk': self.user1.pk}),
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), {'email': ['user with this email already exists.']})

    def test_update_patch_user(self):
        data = {'email': 'new@email.com', 'name': 'new name'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.patch(
            reverse('retrieve-update-destroy', kwargs={'pk': self.user1.pk}),
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.user1.pk)
        self.assertEqual(response.json()['name'], data['name'])
        self.assertEqual(response.json()['email'], data['email'])
        self.assertIsNotNone(response.json()['date_joined'])

    def test_update_patch_another_user(self):
        data = {'email': 'new@email.com', 'name': 'new name'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.patch(
            reverse('retrieve-update-destroy', kwargs={'pk': self.user2.pk}),
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(
            response.json(),
            {'detail': 'You do not have permission to perform this action.'}
        )

    def test_update_patch_unexistent_user(self):
        data = {'email': 'new@email.com', 'name': 'new name'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.patch(
            reverse('retrieve-update-destroy', kwargs={'pk': 99999}),
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(
            response.json(),
            {'detail': 'No CustomUser matches the given query.'}
        )

    def test_update_patch_user_with_email_already_used(self):
        data = {'email': self.user2.email, 'name': 'new name'}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.patch(
            reverse('retrieve-update-destroy', kwargs={'pk': self.user1.pk}),
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), {'email': ['user with this email already exists.']})
