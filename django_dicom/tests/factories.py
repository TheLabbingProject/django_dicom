import glob
import factory
import os

from django_dicom.models import Image

TEST_FILES_PATH = "./tests/files/"
SERIES_DIR = os.path.abspath(os.path.join(TEST_FILES_PATH, "whole_series"))
SERIES_FILES = glob.glob(os.path.join(SERIES_DIR, "*.dcm"))


def get_test_file_path(name: str) -> str:
    file_path = os.path.join(TEST_FILES_PATH, f"{name}.dcm")
    return os.path.abspath(file_path)


class ImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Image
        strategy = factory.BUILD_STRATEGY

    file = factory.django.FileField()
