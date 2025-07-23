from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import AccessToken

from users.models import CustomUser


class QuestionCreateViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = CustomUser.objects.create_superuser(
            name='admin', email='admin@email.com', password='Str0ngP4ssw0rd#123'
        )
        self.admin.access_token = AccessToken.for_user(self.admin)
        self.user = CustomUser.objects.create_user(
            name='johndoe', email='johndoe@email.com', password='Str0ngP4ssw0rd#123'
        )
        self.user.access_token = AccessToken.for_user(self.user)

    def test_create_question_with_admin_user(self):
        data = {
            'stem': '2 + 2 equals',
            'year': 2025,
            'education_level': 'EF',
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.post(reverse('questions-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.json()['id'])
        self.assertEqual(response.json()['stem'], data['stem'])
        self.assertEqual(response.json()['year'], data['year'])
        self.assertEqual(response.json()['education_level'], data['education_level'])

    def test_create_question_with_normal_user(self):
        data = {
            'stem': '2 + 2 equals',
            'year': 2025,
            'education_level': 'EF',
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access_token}')
        response = self.client.post(reverse('questions-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(
            response.json(), {
            'detail': 'You do not have permission to perform this action.'}
        )

    def test_create_question_with_year_in_the_future(self):
        future_year = date.today().year + 1
        data = {
            'stem': '2 + 2 equals',
            'year': future_year,
            'education_level': 'EF',
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.post(reverse('questions-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.json(),
            {'year': ['Question year can not be in the future.']}
        )