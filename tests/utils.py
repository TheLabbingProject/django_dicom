from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model


TEST_PASSWORD = "Aa123456"
User = get_user_model()


class LoggedInTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create_user(
            username="admin",
            email="admin@TheLabbingProject.test",
            password=TEST_PASSWORD,
            is_staff=True,
        )
        self.client.force_authenticate(user)
