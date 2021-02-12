import os
import shutil
import sys

import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test.utils import get_runner


def clean_media():
    media = settings.IMPORTED_PATH
    if "tests" in media:
        shutil.rmtree(media)
    else:
        raise ImproperlyConfigured(
            "Deleting media directory outside of tests environment is forbidden."
        )


if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_settings"
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    clean_media()
    sys.exit(bool(failures))
