import os

from django.contrib.auth import get_user_model
from django_dicom.models import Image
from pathlib import Path
from rest_framework.test import APITestCase


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
    image = Image.objects.get(uid=details["uid"])
    dcm_path = image.dcm.name if os.getenv("USE_S3") else image.dcm.path
    curr_path = Path(dcm_path)
    curr_path.rename(old_path)
    image.dcm = str(old_path)


def seperate_raw_name(raw_name: str, fields: list) -> dict:
    splitted = raw_name.split("^")
    name_dict = {}
    i = 0
    for field in fields:
        name_dict[field] = splitted[i] if i < len(splitted) else ""
        i += 1
    return name_dict
