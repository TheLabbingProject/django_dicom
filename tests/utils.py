from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django_dicom.models import Image
from pathlib import Path


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


def restore_path(details: dict, old_path: str) -> None:
    img = Image.objects.get(uid=details["uid"])
    curr_path = Path(img.dcm.path)
    curr_path.rename(old_path)
    img.dcm = str(old_path)


def seperate_raw_name(raw_name: str, fields: list) -> dict:
    splitted = raw_name.split("^")
    name_dict = {}
    i = 0
    for field in fields:
        name_dict[field] = splitted[i] if i < len(splitted) else ""
        i += 1
    return name_dict
