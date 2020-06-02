import os
import sys
import django
import shutil
from django.conf import settings
from django.test.utils import get_runner


if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_settings"
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    shutil.rmtree(settings.IMPORTED_PATH)
    sys.exit(bool(failures))
