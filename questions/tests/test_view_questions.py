import copy
from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from users.models import CustomUser
from questions.models import Choice, Question


class QuestionCreateViewTestCase(APITestCase):
    def authenticate(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {user.access_token}')

    @classmethod
    def setUpTestData(cls):
        cls.admin = CustomUser.objects.create_superuser(
            name='admin', email='admin@email.com', password='Str0ngP4ssw0rd#123'
        )
        cls.admin.access_token = AccessToken.for_user(cls.admin)
        cls.user = CustomUser.objects.create_user(
            name='johndoe', email='johndoe@email.com', password='Str0ngP4ssw0rd#123'
        )
        cls.user.access_token = AccessToken.for_user(cls.user)
        cls.url = reverse('question-list')

    def setUp(self):
        self.client = APIClient()
        self.base_data = {
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

    def test_create_question_with_admin_user(self):
        data = self.base_data
        self.authenticate(self.admin)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data['stem'], data['stem'])
        self.assertEqual(response.data['year'], data['year'])
        self.assertEqual(response.data['education_level'], data['education_level'])

        question = Question.objects.prefetch_related('choices').get(pk=response.data['id'])
        choices = list(question.choices.order_by('display_order').values('text', 'is_correct', 'display_order'))
        self.assertEqual(choices, data['choices'])

    def test_create_question_with_normal_user(self):
        self.authenticate(self.user)
        response = self.client.post(self.url, data=self.base_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data, {
            'detail': 'You do not have permission to perform this action.'}
        )

    def test_create_question_with_year_in_the_future(self):
        future_year = date.today().year + 1
        data = copy.deepcopy(self.base_data)
        data['year'] = future_year
        self.authenticate(self.admin)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {'year': ['Question year can not be in the future.']}
        )

    def test_create_question_with_less_than_4_choices(self):
        data = copy.deepcopy(self.base_data)
        data['choices'] = data['choices'][:3]
        self.authenticate(self.admin)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'choices': ['A question should have 4 or 5 choices.']})

    def test_create_question_with_more_than_5_choices(self):
        data = copy.deepcopy(self.base_data)
        data['choices'].append({'text': '6', 'is_correct': False, 'display_order': 5},)
        self.authenticate(self.admin)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'choices': ['A question should have 4 or 5 choices.']})

    def test_create_question_with_more_than_one_correct_choice(self):
        data = copy.deepcopy(self.base_data)
        data['choices'][0]['is_correct'] = True
        self.authenticate(self.admin)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {'choices': ['A question should have only one correct choice.']}
        )

    def test_create_question_without_correct_choice(self):
        data = copy.deepcopy(self.base_data)
        data['choices'][3]['is_correct'] = False
        self.authenticate(self.admin)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {'choices': ['A question should have only one correct choice.']}
        )

    def test_create_question_with_repetead_display_order(self):
        data = copy.deepcopy(self.base_data)
        data['choices'][4]['display_order'] = 1
        self.authenticate(self.admin)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {'choices': ['A question cannot have choices with repeated display order.']}
        )


class QuestionRetrieveViewTestCase(APITestCase):
    def authenticate(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {user.access_token}')

    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            name='johndoe', email='johndoe@email.com', password='Str0ngP4ssw0rd#123'
        )
        cls.user.access_token = AccessToken.for_user(cls.user)
        cls.admin = CustomUser.objects.create_superuser(
            name='admin', email='admin@email.com', password='Str0ngP4ssw0rd#123'
        )
        cls.admin.access_token = AccessToken.for_user(cls.admin)
        cls.question = Question.objects.create(
            stem='2 + 2 equals', year=2025, education_level='EF'
        )
        cls.choice1 = Choice.objects.create(question=cls.question, text='1', is_correct=False, display_order=1)
        cls.choice2 = Choice.objects.create(question=cls.question, text='2', is_correct=False, display_order=2)
        cls.choice3 = Choice.objects.create(question=cls.question, text='3', is_correct=False, display_order=3)
        cls.choice4 = Choice.objects.create(question=cls.question, text='4', is_correct=True, display_order=4)
        cls.choice5 = Choice.objects.create(question=cls.question, text='5', is_correct=False, display_order=5)
        cls.url = reverse('question-detail', kwargs={'pk': cls.question.id})

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_question_with_normal_user(self):
        self.authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.question.id)
        self.assertEqual(response.data['stem'], self.question.stem)
        self.assertEqual(response.data['year'], self.question.year)
        self.assertEqual(response.data['education_level'], self.question.education_level)

        question = Question.objects.prefetch_related('choices').get(pk=response.data['id'])
        choices = list(question.choices.order_by('display_order').values('id', 'text', 'display_order'))
        self.assertEqual(response.data['choices'], choices)

    def test_retrieve_question_with_admin_user(self):
        self.authenticate(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.question.id)
        self.assertEqual(response.data['stem'], self.question.stem)
        self.assertEqual(response.data['year'], self.question.year)
        self.assertEqual(response.data['education_level'], self.question.education_level)

        question = Question.objects.prefetch_related('choices').get(pk=response.data['id'])
        choices = list(question.choices.order_by('display_order').values('id', 'text', 'display_order', 'is_correct'))
        self.assertEqual(response.data['choices'], choices)

    def test_retrieve_unexistent_question(self):
        question_id = 999999
        self.authenticate(self.user)
        response = self.client.get(reverse('question-detail', kwargs={'pk': question_id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'detail': 'No Question matches the given query.'})

    def test_retrieve_question_with_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'detail': 'Authentication credentials were not provided.'})


class QuestionDestroyViewTestCase(APITestCase):
    def authenticate(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {user.access_token}')

    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            name='johndoe', email='johndoe@email.com', password='Str0ngP4ssw0rd#123'
        )
        cls.user.access_token = AccessToken.for_user(cls.user)
        cls.admin = CustomUser.objects.create_superuser(
            name='admin', email='admin@email.com', password='Str0ngP4ssw0rd#123'
        )
        cls.admin.access_token = AccessToken.for_user(cls.admin)
        cls.question = Question.objects.create(
            stem='2 + 2 equals', year=2025, education_level='EF'
        )
        cls.choice1 = Choice.objects.create(question=cls.question, text='1', is_correct=False, display_order=1)
        cls.choice2 = Choice.objects.create(question=cls.question, text='2', is_correct=False, display_order=2)
        cls.choice3 = Choice.objects.create(question=cls.question, text='3', is_correct=False, display_order=3)
        cls.choice4 = Choice.objects.create(question=cls.question, text='4', is_correct=True, display_order=4)
        cls.choice5 = Choice.objects.create(question=cls.question, text='5', is_correct=False, display_order=5)
        cls.url = reverse('question-detail', kwargs={'pk': cls.question.id})

    def setUp(self):
        self.client = APIClient()

    def test_delete_question_with_admin_user(self):
        self.authenticate(self.admin)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(response.data)

    def test_delete_question_with_normal_user(self):
        self.authenticate(self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data,
            {'detail': 'You do not have permission to perform this action.'}
        )

    def test_delete_question_with_unauthenticated_user(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'detail': 'Authentication credentials were not provided.'})

    def test_delete_unexistent_question(self):
        question_id = 9999999
        self.authenticate(self.admin)
        response = self.client.delete(reverse('question-detail', kwargs={'pk': question_id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'detail': 'No Question matches the given query.'})


class QuestionUpdateViewTestCase(APITestCase):
    def authenticate(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {user.access_token}')

    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            name='johndoe', email='johndoe@email.com', password='Str0ngP4ssw0rd#123'
        )
        cls.user.access_token = AccessToken.for_user(cls.user)
        cls.admin = CustomUser.objects.create_superuser(
            name='admin', email='admin@email.com', password='Str0ngP4ssw0rd#123'
        )
        cls.admin.access_token = AccessToken.for_user(cls.admin)
        cls.question = Question.objects.create(
            stem='2 + 2 equals', year=2025, education_level='EF'
        )
        cls.choice1 = Choice.objects.create(question=cls.question, text='1', is_correct=False, display_order=1)
        cls.choice2 = Choice.objects.create(question=cls.question, text='2', is_correct=False, display_order=2)
        cls.choice3 = Choice.objects.create(question=cls.question, text='3', is_correct=False, display_order=3)
        cls.choice4 = Choice.objects.create(question=cls.question, text='4', is_correct=False, display_order=4)
        cls.choice5 = Choice.objects.create(question=cls.question, text='5', is_correct=True, display_order=5)
        cls.url = reverse('question-detail', kwargs={'pk': cls.question.id})
        cls.base_data = {
            'stem': cls.question.stem,
            'year': cls.question.year,
            'education_level': cls.question.education_level,
            'choices': [
                {'id': cls.question.choices.all()[0].id, 'text': '1', 'is_correct': False, 'display_order': 1},
                {'id': cls.question.choices.all()[1].id, 'text': '2', 'is_correct': False, 'display_order': 2},
                {'id': cls.question.choices.all()[2].id, 'text': '3', 'is_correct': False, 'display_order': 3},
                {'id': cls.question.choices.all()[3].id, 'text': '4', 'is_correct': True, 'display_order': 4},
                {'id': cls.question.choices.all()[4].id, 'text': '5', 'is_correct': False, 'display_order': 5},
            ]
        }

    def setUp(self):
        self.client = APIClient()

    def test_update_question_with_admin_user(self):
        data = self.base_data
        self.authenticate(self.admin)
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.question.id)
        self.assertEqual(response.data['stem'], data['stem'])
        self.assertEqual(response.data['year'], data['year'])
        self.assertEqual(response.data['education_level'], data['education_level'])

        self.question.refresh_from_db()
        choices = list(self.question.choices.order_by('display_order').values('id', 'text', 'is_correct', 'display_order'))
        self.assertEqual(choices, data['choices'])

    def test_update_question_with_normal_user(self):
        data = self.base_data
        self.authenticate(self.user)
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data,
            {'detail': 'You do not have permission to perform this action.'}
        )

    def test_update_question_with_missing_choice(self):
        data = copy.deepcopy(self.base_data)
        data['choices'] = data['choices'][:4]
        self.authenticate(self.admin)
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        missing_choice_id = self.question.choices.all()[4].id
        self.assertEqual(
            response.data,
            {'choices': [f'Choices id [{missing_choice_id}] not present in new question data.']}
        )

    def test_update_question_with_year_in_the_future(self):
        data = copy.deepcopy(self.base_data)
        data['year'] = date.today().year + 1
        self.authenticate(self.admin)
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {'year': ['Question year can not be in the future.']}
        )

    def test_update_question_with_less_than_4_choices(self):
        data = copy.deepcopy(self.base_data)
        data['choices'] = data['choices'][:3]
        self.authenticate(self.admin)
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {'choices': ['A question should have 4 or 5 choices.']}
        )

    def test_update_question_with_more_than_5_choices(self):
        data = copy.deepcopy(self.base_data)
        data['choices'].append({'text': '6', 'is_correct': False, 'display_order': 5})
        self.authenticate(self.admin)
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {'choices': ['A question should have 4 or 5 choices.']}
        )

    def test_update_question_with_repeated_choice_id(self):
        data = copy.deepcopy(self.base_data)

        repeated_choice = data['choices'][0].copy()
        missing_choice = data['choices'][1]
        missing_choice_id = missing_choice['id']
        repeated_choice['display_order'] = missing_choice['display_order']
        data['choices'][1] = repeated_choice

        self.authenticate(self.admin)
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {'choices': [f'Choices id [{missing_choice_id}] not present in new question data.']}
        )

    def test_update_unexistent_question(self):
        data = self.base_data
        question_id = 9999999
        self.authenticate(self.admin)
        response = self.client.put(
            reverse('question-detail', kwargs={'pk': question_id}), data=data
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'detail': 'No Question matches the given query.'})
