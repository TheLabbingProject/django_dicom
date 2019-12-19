# from rest_framework.test import APITestCase, APIClient

from django.test import TestCase
from django.contrib import auth

# from django.contrib.auth import get_user_model


TEST_PASSWORD = "Aa123456"
# User = get_user_model()


class MockRequest:
    pass


class LoggedInTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin", email="admin@LabbingProject.test", password=TEST_PASSWORD
        )
        self.login()

    def login(self):
        # self.client.login(username=self.user.username, password=TEST_PASSWORD)
        self.client.login(username=self.user.username)
