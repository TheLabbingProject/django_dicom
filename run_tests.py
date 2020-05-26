import os
import sys
from pathlib import Path
from tests.fixtures import (
    TEST_SERIES_FIELDS,
    TEST_DWI_SERIES_FIELDS,
    TEST_PATIENT_FIELDS,
)

import django
from django.conf import settings
from django.test.utils import get_runner


def clean_media():
    media = (
        Path(settings.MEDIA_ROOT)
        / "MRI/DICOM"
        / TEST_PATIENT_FIELDS["uid"]
        / TEST_SERIES_FIELDS["uid"]
    )
    media_dwi = (
        Path(settings.MEDIA_ROOT)
        / "MRI/DICOM"
        / TEST_PATIENT_FIELDS["uid"]
        / TEST_DWI_SERIES_FIELDS["uid"]
    )
    media.rmdir()

    while str(media_dwi) != settings.MEDIA_ROOT:
        media_dwi.rmdir()
        media_dwi = media_dwi.parent


if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_settings"
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    clean_media()
    sys.exit(bool(failures))
