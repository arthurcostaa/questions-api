from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from users.models import CustomUser
from questions.models import Choice, Question, UserAnswer

class UserAnswerViewSetTestCase(APITestCase):
    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access_token}')

    @classmethod
    def setUpTestData(cls):
        cls.question = Question.objects.create(stem='1 + 1 equals', year=2025, education_level='EF')
        cls.choice1 = Choice.objects.create(question=cls.question, text='1', is_correct=False, display_order=1)
        cls.choice2 = Choice.objects.create(question=cls.question, text='2', is_correct=True, display_order=2)
        cls.choice3 = Choice.objects.create(question=cls.question, text='3', is_correct=False, display_order=3)
        cls.choice4 = Choice.objects.create(question=cls.question, text='4', is_correct=False, display_order=4)

        cls.question2 = Question.objects.create(stem='2 + 2 equals', year=2025, education_level='EF')
        cls.choice5 = Choice.objects.create(question=cls.question2, text='1', is_correct=False, display_order=1)
        cls.choice6 = Choice.objects.create(question=cls.question2, text='2', is_correct=False, display_order=2)
        cls.choice7 = Choice.objects.create(question=cls.question2, text='3', is_correct=False, display_order=3)
        cls.choice8 = Choice.objects.create(question=cls.question2, text='4', is_correct=True, display_order=4)

        cls.user = CustomUser.objects.create_user(email='test@email.com', name='test', password='Str0ng#P4ssw0d!123')
        cls.user.access_token = AccessToken.for_user(cls.user)
        cls.url = reverse('question-answer-list', kwargs={'question_pk': cls.question.id})

    def setUp(self):
        self.client = APIClient()

    def test_answer_question_with_correct_reponse(self):
        data = {'choice': self.question.choices.get(is_correct=True).id}
        self.authenticate()
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['choice'], data['choice'])
        self.assertTrue(response.data['is_correct'])
        self.assertIsNotNone(response.data['answered_at'])

    def test_answer_question_with_wrong_reponse(self):
        data = {'choice': self.question.choices.filter(is_correct=False).first().id}
        self.authenticate()
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['choice'], data['choice'])
        self.assertFalse(response.data['is_correct'])
        self.assertIsNotNone(response.data['answered_at'])

    def test_answer_question_with_unauthenticated_user(self):
        data = {'choice': self.choice2.id}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'detail': 'Authentication credentials were not provided.'})

    def test_answer_question_with_unexistent_question(self):
        data = {'choice': self.choice1.id}
        self.authenticate()
        response = self.client.post(
            reverse('question-answer-list', kwargs={'question_pk': 99999}),
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'detail': 'No Question matches the given query.'})

    def test_answer_question_with_unexistent_choice(self):
        choice_id = 999
        self.authenticate()
        response = self.client.post(self.url, data={'choice': choice_id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'choice': [f'Invalid pk "{choice_id}" - object does not exist.']})

    def test_answer_question_with_choice_of_another_question(self):
        data = {'choice': self.choice5.id}
        self.authenticate()
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {'error': ["This choice doesn't belong to this question."]})

    def test_answer_question_twice(self):
        UserAnswer.objects.create(question=self.question, choice=self.choice1, user=self.user)
        data = {'choice': self.choice1.id}
        self.authenticate()
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {'error': ['Question already answered by the user.']})
