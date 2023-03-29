import contextlib
import os
import shutil
import sys

import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test.utils import get_runner

PROTECTED_MEDIA = "Deleting media directory outside of tests environment is forbidden."


def clean_media():
    media = settings.IMPORTED_PATH
    if "tests" not in media:
        raise ImproperlyConfigured(PROTECTED_MEDIA)
    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree(media)


if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_settings"
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    clean_media()
    sys.exit(bool(failures))
