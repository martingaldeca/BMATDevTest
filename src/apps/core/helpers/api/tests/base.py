from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase

from core.factories import UserFactory


class APITestBase(APITestCase):
    url = None

    def setUp(self) -> None:
        self.user: User = UserFactory(password='root1234')
        self.client.login(username=self.user.username, password='root1234')
        response = self.client.post(
            reverse('login'),
            {
                'username': self.user.username,
                'password': 'root1234'
            }
        )
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.request = APIRequestFactory().get(self.url)
        self.request.user = self.user
        self.test_context = {'request': self.request}

    def assertSameFile(self, file1, file2):
        file1.seek(0)
        file2.seek(0)
        self.assertEqual(file1.read(), file2.read())


class SerializerTestBase(TestCase):
    def setUp(self) -> None:
        self.user: User = UserFactory()
        self.request = APIRequestFactory().post('/foo', data=None)
        self.request.user = self.user
        self.context = {
            'request': self.request
        }
