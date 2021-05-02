from django.test import TestCase, Client
from posts.models import User


class TestUser(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test_user",
            email="test_user@yatube.com",
            password="test"
        )

    def testRegistration(self):
        response = self.client.get('/test_user/')

        self.assertEqual(
            response.status_code,
            200,
            msg='Не найдена страница созданного пользователя.'
        )
