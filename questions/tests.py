from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import AccessToken

from users.models import CustomUser
from questions.models import Choice, Question


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
            'choices': [
                {'text': '1', 'is_correct': False, 'display_order': 1},
                {'text': '2', 'is_correct': False, 'display_order': 2},
                {'text': '3', 'is_correct': False, 'display_order': 3},
                {'text': '4', 'is_correct': True, 'display_order': 4},
                {'text': '5', 'is_correct': False, 'display_order': 5}
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.post(reverse('questions-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.json()['id'])
        self.assertEqual(response.json()['stem'], data['stem'])
        self.assertEqual(response.json()['year'], data['year'])
        self.assertEqual(response.json()['education_level'], data['education_level'])

        question = Question.objects.get(pk=response.data['id'])
        choices = list(question.choices.order_by('display_order').values('text', 'is_correct', 'display_order'))
        self.assertEqual(choices, data['choices'])

    def test_create_question_with_normal_user(self):
        data = {
            'stem': '2 + 2 equals',
            'year': 2025,
            'education_level': 'EF',
            'choices': [
                {'text': '1', 'is_correct': False, 'display_order': 1},
                {'text': '2', 'is_correct': False, 'display_order': 2},
                {'text': '3', 'is_correct': False, 'display_order': 3},
                {'text': '4', 'is_correct': True, 'display_order': 4},
                {'text': '5', 'is_correct': False, 'display_order': 5},
            ]
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
            'choices': [
                {'text': '1', 'is_correct': False, 'display_order': 1},
                {'text': '2', 'is_correct': False, 'display_order': 2},
                {'text': '3', 'is_correct': False, 'display_order': 3},
                {'text': '4', 'is_correct': True, 'display_order': 4},
                {'text': '5', 'is_correct': False, 'display_order': 5},
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.post(reverse('questions-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.json(),
            {'year': ['Question year can not be in the future.']}
        )

    def test_create_question_with_less_than_4_choices(self):
        data = {
            'stem': '2 + 2 equals',
            'year': 2025,
            'education_level': 'EF',
            'choices': [
                {'text': '1', 'is_correct': False, 'display_order': 1},
                {'text': '2', 'is_correct': False, 'display_order': 2},
                {'text': '4', 'is_correct': True, 'display_order': 3},
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.post(reverse('questions-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), {'choices': ['A question should have 4 or 5 choices.']})

    def test_create_question_with_more_than_5_choices(self):
        data = {
            'stem': '2 + 2 equals',
            'year': 2025,
            'education_level': 'EF',
            'choices': [
                {'text': '1', 'is_correct': False, 'display_order': 1},
                {'text': '2', 'is_correct': False, 'display_order': 2},
                {'text': '3', 'is_correct': False, 'display_order': 3},
                {'text': '4', 'is_correct': True, 'display_order': 4},
                {'text': '5', 'is_correct': False, 'display_order': 5},
                {'text': '6', 'is_correct': False, 'display_order': 5},
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.post(reverse('questions-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), {'choices': ['A question should have 4 or 5 choices.']})

    def test_create_question_with_more_than_one_correct_choice(self):
        data = {
            'stem': '2 + 2 equals',
            'year': 2025,
            'education_level': 'EF',
            'choices': [
                {'text': '1', 'is_correct': False, 'display_order': 1},
                {'text': '2', 'is_correct': False, 'display_order': 2},
                {'text': '3', 'is_correct': False, 'display_order': 3},
                {'text': '4', 'is_correct': True, 'display_order': 4},
                {'text': '5', 'is_correct': True, 'display_order': 5},
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.post(reverse('questions-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.json(),
            {'choices': ['A question should have only one correct choice.']}
        )

    def test_create_question_without_correct_choice(self):
        data = {
            'stem': '2 + 2 equals',
            'year': 2025,
            'education_level': 'EF',
            'choices': [
                {'text': '1', 'is_correct': False, 'display_order': 1},
                {'text': '2', 'is_correct': False, 'display_order': 2},
                {'text': '3', 'is_correct': False, 'display_order': 3},
                {'text': '4', 'is_correct': False, 'display_order': 4},
                {'text': '5', 'is_correct': False, 'display_order': 5},
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.post(reverse('questions-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.json(),
            {'choices': ['A question should have only one correct choice.']}
        )

    def test_create_question_with_repetead_display_order(self):
        data = {
            'stem': '2 + 2 equals',
            'year': 2025,
            'education_level': 'EF',
            'choices': [
                {'text': '1', 'is_correct': False, 'display_order': 1},
                {'text': '2', 'is_correct': False, 'display_order': 2},
                {'text': '3', 'is_correct': False, 'display_order': 3},
                {'text': '4', 'is_correct': True, 'display_order': 4},
                {'text': '5', 'is_correct': False, 'display_order': 1},
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.post(reverse('questions-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.json(),
            {'choices': ['A question cannot have choices with repeated display order.']}
        )


class QuestionRetrieveViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            name='johndoe', email='johndoe@email.com', password='Str0ngP4ssw0rd#123'
        )
        self.user.access_token = AccessToken.for_user(self.user)
        self.admin = CustomUser.objects.create_superuser(
            name='admin', email='admin@email.com', password='Str0ngP4ssw0rd#123'
        )
        self.admin.access_token = AccessToken.for_user(self.admin)
        self.question = Question.objects.create(
            stem='2 + 2 equals', year=2025, education_level='EF'
        )
        self.choice1 = Choice.objects.create(question=self.question, text='1', is_correct=False, display_order=1)
        self.choice2 = Choice.objects.create(question=self.question, text='2', is_correct=False, display_order=2)
        self.choice3 = Choice.objects.create(question=self.question, text='3', is_correct=False, display_order=3)
        self.choice4 = Choice.objects.create(question=self.question, text='4', is_correct=True, display_order=4)
        self.choice5 = Choice.objects.create(question=self.question, text='5', is_correct=False, display_order=5)

    def test_retrieve_question_with_normal_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access_token}')
        response = self.client.get(
            reverse('questions-detail', kwargs={'pk': self.question.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.question.id)
        self.assertEqual(response.data['stem'], self.question.stem)
        self.assertEqual(response.data['year'], self.question.year)
        self.assertEqual(response.data['education_level'], self.question.education_level)

        self.assertEqual(response.data['choices'][0]['text'], self.choice1.text)
        self.assertEqual(response.data['choices'][0]['display_order'], self.choice1.display_order)
        self.assertIsNone(response.data['choices'][0].get('is_correct'))

        self.assertEqual(response.data['choices'][1]['text'], self.choice2.text)
        self.assertEqual(response.data['choices'][1]['display_order'], self.choice2.display_order)
        self.assertIsNone(response.data['choices'][1].get('is_correct'))

        self.assertEqual(response.data['choices'][2]['text'], self.choice3.text)
        self.assertEqual(response.data['choices'][2]['display_order'], self.choice3.display_order)
        self.assertIsNone(response.data['choices'][2].get('is_correct'))

        self.assertEqual(response.data['choices'][3]['text'], self.choice4.text)
        self.assertEqual(response.data['choices'][3]['display_order'], self.choice4.display_order)
        self.assertIsNone(response.data['choices'][3].get('is_correct'))

        self.assertEqual(response.data['choices'][4]['text'], self.choice5.text)
        self.assertEqual(response.data['choices'][4]['display_order'], self.choice5.display_order)
        self.assertIsNone(response.data['choices'][4].get('is_correct'))

    def test_retrieve_question_with_admin_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.get(
            reverse('questions-detail', kwargs={'pk': self.question.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.question.id)
        self.assertEqual(response.data['stem'], self.question.stem)
        self.assertEqual(response.data['year'], self.question.year)
        self.assertEqual(response.data['education_level'], self.question.education_level)

        self.assertEqual(response.data['choices'][0]['text'], self.choice1.text)
        self.assertEqual(response.data['choices'][0]['display_order'], self.choice1.display_order)
        self.assertEqual(response.data['choices'][0]['is_correct'], self.choice1.is_correct)

        self.assertEqual(response.data['choices'][1]['text'], self.choice2.text)
        self.assertEqual(response.data['choices'][1]['display_order'], self.choice2.display_order)
        self.assertEqual(response.data['choices'][1]['is_correct'], self.choice2.is_correct)

        self.assertEqual(response.data['choices'][2]['text'], self.choice3.text)
        self.assertEqual(response.data['choices'][2]['display_order'], self.choice3.display_order)
        self.assertEqual(response.data['choices'][2]['is_correct'], self.choice3.is_correct)

        self.assertEqual(response.data['choices'][3]['text'], self.choice4.text)
        self.assertEqual(response.data['choices'][3]['display_order'], self.choice4.display_order)
        self.assertEqual(response.data['choices'][3]['is_correct'], self.choice4.is_correct)

        self.assertEqual(response.data['choices'][4]['text'], self.choice5.text)
        self.assertEqual(response.data['choices'][4]['display_order'], self.choice5.display_order)
        self.assertEqual(response.data['choices'][4]['is_correct'], self.choice5.is_correct)

    def test_retrieve_unexistent_question(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access_token}')
        response = self.client.get(
            reverse('questions-detail', kwargs={'pk': 999999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.json(), {'detail': 'No Question matches the given query.'})

    def test_retrieve_question_with_unauthenticated_user(self):
        response = self.client.get(
            reverse('questions-detail', kwargs={'pk': self.question.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})


class QuestionDestroyViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            name='johndoe', email='johndoe@email.com', password='Str0ngP4ssw0rd#123'
        )
        self.user.access_token = AccessToken.for_user(self.user)
        self.admin = CustomUser.objects.create_superuser(
            name='admin', email='admin@email.com', password='Str0ngP4ssw0rd#123'
        )
        self.admin.access_token = AccessToken.for_user(self.admin)
        self.question = Question.objects.create(
            stem='2 + 2 equals', year=2025, education_level='EF'
        )
        self.choice1 = Choice.objects.create(question=self.question, text='1', is_correct=False, display_order=1)
        self.choice2 = Choice.objects.create(question=self.question, text='2', is_correct=False, display_order=2)
        self.choice3 = Choice.objects.create(question=self.question, text='3', is_correct=False, display_order=3)
        self.choice4 = Choice.objects.create(question=self.question, text='4', is_correct=True, display_order=4)
        self.choice5 = Choice.objects.create(question=self.question, text='5', is_correct=False, display_order=5)

    def test_delete_question_with_admin_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.delete(
            reverse('questions-detail', kwargs={'pk': self.question.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_question_with_normal_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access_token}')
        response = self.client.delete(
            reverse('questions-detail', kwargs={'pk': self.question.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(
            response.json(),
            {'detail': 'You do not have permission to perform this action.'}
        )

    def test_delete_question_with_unauthenticated_user(self):
        response = self.client.delete(
            reverse('questions-detail', kwargs={'pk': self.question.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_delete_unexistent_question(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.delete(
            reverse('questions-detail', kwargs={'pk': 9999999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.json(), {'detail': 'No Question matches the given query.'})


class QuestionUpdateViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            name='johndoe', email='johndoe@email.com', password='Str0ngP4ssw0rd#123'
        )
        self.user.access_token = AccessToken.for_user(self.user)
        self.admin = CustomUser.objects.create_superuser(
            name='admin', email='admin@email.com', password='Str0ngP4ssw0rd#123'
        )
        self.admin.access_token = AccessToken.for_user(self.admin)
        self.question = Question.objects.create(
            stem='2 + 2 equals', year=2025, education_level='EF'
        )
        self.choice1 = Choice.objects.create(question=self.question, text='1', is_correct=False, display_order=1)
        self.choice2 = Choice.objects.create(question=self.question, text='2', is_correct=False, display_order=2)
        self.choice3 = Choice.objects.create(question=self.question, text='3', is_correct=False, display_order=3)
        self.choice4 = Choice.objects.create(question=self.question, text='4', is_correct=False, display_order=4)
        self.choice5 = Choice.objects.create(question=self.question, text='5', is_correct=True, display_order=5)

    def test_update_question_with_admin_user(self):
        data = {
            'stem': self.question.stem,
            'year': self.question.year,
            'education_level': self.question.education_level,
            'choices': [
                {'id': self.question.choices.all()[0].id, 'text': '1', 'is_correct': False, 'display_order': 1},
                {'id': self.question.choices.all()[1].id, 'text': '2', 'is_correct': False, 'display_order': 2},
                {'id': self.question.choices.all()[2].id, 'text': '3', 'is_correct': False, 'display_order': 3},
                {'id': self.question.choices.all()[3].id, 'text': '4', 'is_correct': True, 'display_order': 4},
                {'id': self.question.choices.all()[4].id, 'text': '5', 'is_correct': False, 'display_order': 5},
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.put(
            reverse('questions-detail', kwargs={'pk': self.question.id}), data=data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.question.id)
        self.assertEqual(response.data['stem'], data['stem'])
        self.assertEqual(response.data['year'], data['year'])
        self.assertEqual(response.data['education_level'], data['education_level'])

        self.question.refresh_from_db()
        choices = list(self.question.choices.order_by('display_order').values('id', 'text', 'is_correct', 'display_order'))
        self.assertEqual(choices, data['choices'])

    def test_update_question_with_normal_user(self):
        data = {
            'stem': self.question.stem,
            'year': self.question.year,
            'education_level': self.question.education_level,
            'choices': [
                {'id': self.question.choices.all()[0].id, 'text': '1', 'is_correct': False, 'display_order': 1},
                {'id': self.question.choices.all()[1].id, 'text': '2', 'is_correct': False, 'display_order': 2},
                {'id': self.question.choices.all()[2].id, 'text': '3', 'is_correct': False, 'display_order': 3},
                {'id': self.question.choices.all()[3].id, 'text': '4', 'is_correct': True, 'display_order': 4},
                {'id': self.question.choices.all()[4].id, 'text': '5', 'is_correct': False, 'display_order': 5},
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access_token}')
        response = self.client.put(
            reverse('questions-detail', kwargs={'pk': self.question.id}), data=data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(
            response.json(),
            {'detail': 'You do not have permission to perform this action.'}
        )

    def test_update_question_with_missing_choice(self):
        data = {
            'stem': self.question.stem,
            'year': self.question.year,
            'education_level': self.question.education_level,
            'choices': [
                {'id': self.question.choices.all()[0].id, 'text': '1', 'is_correct': False, 'display_order': 1},
                {'id': self.question.choices.all()[1].id, 'text': '2', 'is_correct': False, 'display_order': 2},
                {'id': self.question.choices.all()[2].id, 'text': '3', 'is_correct': False, 'display_order': 3},
                {'id': self.question.choices.all()[3].id, 'text': '4', 'is_correct': True, 'display_order': 4},
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.put(
            reverse('questions-detail', kwargs={'pk': self.question.id}), data=data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        missing_choice_id = self.question.choices.all()[4].id
        self.assertDictEqual(
            response.json(),
            {'choices': [f'Choices id [{missing_choice_id}] not present in new question data.']}
        )

    def test_update_question_with_year_in_the_future(self):
        data = {
            'stem': self.question.stem,
            'year': date.today().year + 1,
            'education_level': self.question.education_level,
            'choices': [
                {'id': self.question.choices.all()[0].id, 'text': '1', 'is_correct': False, 'display_order': 1},
                {'id': self.question.choices.all()[1].id, 'text': '2', 'is_correct': False, 'display_order': 2},
                {'id': self.question.choices.all()[2].id, 'text': '3', 'is_correct': False, 'display_order': 3},
                {'id': self.question.choices.all()[3].id, 'text': '4', 'is_correct': True, 'display_order': 4},
                {'id': self.question.choices.all()[4].id, 'text': '5', 'is_correct': False, 'display_order': 5},
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.put(
            reverse('questions-detail', kwargs={'pk': self.question.id}), data=data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.json(),
            {'year': ['Question year can not be in the future.']}
        )

    def test_update_question_with_less_than_4_choices(self):
        data = {
            'stem': self.question.stem,
            'year': self.question.year,
            'education_level': self.question.education_level,
            'choices': [
                {'id': self.question.choices.all()[0].id, 'text': '1', 'is_correct': False, 'display_order': 1},
                {'id': self.question.choices.all()[1].id, 'text': '2', 'is_correct': False, 'display_order': 2},
                {'id': self.question.choices.all()[2].id, 'text': '3', 'is_correct': False, 'display_order': 3},
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.put(
            reverse('questions-detail', kwargs={'pk': self.question.id}), data=data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.json(),
            {'choices': ['A question should have 4 or 5 choices.']}
        )

    def test_update_question_with_more_than_5_choices(self):
        data = {
            'stem': self.question.stem,
            'year': self.question.year,
            'education_level': self.question.education_level,
            'choices': [
                {'id': self.question.choices.all()[0].id, 'text': '1', 'is_correct': False, 'display_order': 1},
                {'id': self.question.choices.all()[1].id, 'text': '2', 'is_correct': False, 'display_order': 2},
                {'id': self.question.choices.all()[2].id, 'text': '3', 'is_correct': False, 'display_order': 3},
                {'id': self.question.choices.all()[3].id, 'text': '4', 'is_correct': True, 'display_order': 4},
                {'id': self.question.choices.all()[4].id, 'text': '5', 'is_correct': False, 'display_order': 5},
                {'text': '6', 'is_correct': False, 'display_order': 5},
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.put(
            reverse('questions-detail', kwargs={'pk': self.question.id}), data=data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.json(),
            {'choices': ['A question should have 4 or 5 choices.']}
        )

    def test_update_question_with_repeated_choice_id(self):
        repeated_choice_id = self.question.choices.all()[0].id
        missing_choice_id = self.question.choices.all()[1].id
        data = {
            'stem': self.question.stem,
            'year': self.question.year,
            'education_level': self.question.education_level,
            'choices': [
                {'id': repeated_choice_id, 'text': '1', 'is_correct': False, 'display_order': 1},
                {'id': repeated_choice_id, 'text': '1', 'is_correct': False, 'display_order': 2},
                {'id': self.question.choices.all()[2].id, 'text': '3', 'is_correct': False, 'display_order': 3},
                {'id': self.question.choices.all()[3].id, 'text': '4', 'is_correct': True, 'display_order': 4},
                {'id': self.question.choices.all()[4].id, 'text': '5', 'is_correct': False, 'display_order': 5},
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.put(
            reverse('questions-detail', kwargs={'pk': self.question.id}), data=data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.json(),
            {'choices': [f'Choices id [{missing_choice_id}] not present in new question data.']}
        )

    def test_update_unexistent_question(self):
        data = {
            'stem': self.question.stem,
            'year': self.question.year,
            'education_level': self.question.education_level,
            'choices': [
                {'id': self.question.choices.all()[0].id, 'text': '1', 'is_correct': False, 'display_order': 1},
                {'id': self.question.choices.all()[1].id, 'text': '1', 'is_correct': False, 'display_order': 2},
                {'id': self.question.choices.all()[2].id, 'text': '3', 'is_correct': False, 'display_order': 3},
                {'id': self.question.choices.all()[3].id, 'text': '4', 'is_correct': True, 'display_order': 4},
                {'id': self.question.choices.all()[4].id, 'text': '5', 'is_correct': False, 'display_order': 5},
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin.access_token}')
        response = self.client.put(
            reverse('questions-detail', kwargs={'pk': 9999999}), data=data
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.json(), {'detail': 'No Question matches the given query.'})
