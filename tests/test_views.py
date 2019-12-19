from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from .fixtures import (
    TEST_IMAGE_FIELDS,
    TEST_SERIES_FIELDS,
    TEST_STUDY_FIELDS,
    TEST_PATIENT_FIELDS,
)
from django_dicom.models import Series, Study, Patient, Image
from .utils import LoggedInTestCase


class LoggedOutImageViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Creates instances to be used in the tests.
        For more information see Django's :class:`~django.test.TestCase` documentation_.

        .. _documentation: https://docs.djangoproject.com/en/2.2/topics/testing/tools/#testcase
        """
        TEST_SERIES_FIELDS["patient"] = Patient.objects.create(**TEST_PATIENT_FIELDS)
        TEST_SERIES_FIELDS["study"] = Study.objects.create(**TEST_STUDY_FIELDS)
        TEST_IMAGE_FIELDS["series"] = Series.objects.create(**TEST_SERIES_FIELDS)
        Image.objects.create(**TEST_IMAGE_FIELDS)

    def setUp(self):
        self.test_instance = Image.objects.get(uid=TEST_IMAGE_FIELDS["uid"])

    def test_image_list_redirects_to_login(self):
        url = reverse("dicom:image-list")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_image_detail_redirects_to_login(self):
        url = self.test_instance.get_absolute_url()
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_image_create_redirects_to_login(self):
    #     url = reverse("image_create")
    #     response = self.client.get(url, follow=True)
    #     self.assertEqual(response.status_code, 401)


class LoggedInImageViewTestCase(LoggedInTestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Creates instances to be used in the tests.
        For more information see Django's :class:`~django.test.TestCase` documentation_.

        .. _documentation: https://docs.djangoproject.com/en/2.2/topics/testing/tools/#testcase
        """
        TEST_SERIES_FIELDS["patient"] = Patient.objects.create(**TEST_PATIENT_FIELDS)
        TEST_SERIES_FIELDS["study"] = Study.objects.create(**TEST_STUDY_FIELDS)
        TEST_IMAGE_FIELDS["series"] = Series.objects.create(**TEST_SERIES_FIELDS)
        Image.objects.create(**TEST_IMAGE_FIELDS)

    def setUp(self):
        self.test_instance = Image.objects.get(uid=TEST_IMAGE_FIELDS["uid"])
        super(LoggedInImageViewTestCase, self).setUp()

    def test_list_view(self):
        response = self.client.get(reverse("dicom:image-list"))
        print(
            "++++++++++++++++++++++++++++++++++",
            response.content,
            "++++++++++++++++++++++++++++++++++",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertTemplateUsed(response, "dicom/images/image_list.html")

    def test_detail_view(self):
        url = self.test_instance.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertTemplateUsed(response, "dicom/images/image_detail.html")

    # def test_create_view(self):
    #     url = reverse("instances_create")
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "dicom/instances/instances_create.html")


# class LoggedOutSeriesViewTestCase(TestCase):
#     def setUp(self):
#         instance = ImageFactory(file__from_path=get_test_file_path("test"))
#         instance.save()
#         self.test_series = instance.series

#     def test_series_list_redirects_to_login(self):
#         url = reverse("series_list")
#         response = self.client.get(url, follow=True)
#         self.assertRedirects(response, f"/accounts/login/?next={url}")

#     def test_series_detail_redirects_to_login(self):
#         url = self.test_series.get_absolute_url()
#         response = self.client.get(url, follow=True)
#         self.assertRedirects(response, f"/accounts/login/?next={url}")


# class LoggedInSeriesViewTestCase(LoggedInTestCase):
#     def setUp(self):
#         instance = ImageFactory(file__from_path=get_test_file_path("test"))
#         instance.save()
#         self.test_series = instance.series
#         super(LoggedInSeriesViewTestCase, self).setUp()

#     def test_list_view(self):
#         response = self.client.get(reverse("series_list"))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "dicom/series/series_list.html")

#     def test_detail_view(self):
#         url = self.test_series.get_absolute_url()
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "dicom/series/series_detail.html")


# class LoggedOutPatientViewTestCase(TestCase):
#     def setUp(self):
#         instance = ImageFactory(file__from_path=get_test_file_path("test"))
#         instance.save()
#         self.test_patient = instance.patient

#     def test_patient_list_redirects_to_login(self):
#         url = reverse("patient_list")
#         response = self.client.get(url, follow=True)
#         self.assertRedirects(response, f"/accounts/login/?next={url}")

#     def test_patient_detail_redirects_to_login(self):
#         url = self.test_patient.get_absolute_url()
#         response = self.client.get(url, follow=True)
#         self.assertRedirects(response, f"/accounts/login/?next={url}")


# class LoggedInPatientViewTestCase(LoggedInTestCase):
#     def setUp(self):
#         instance = ImageFactory(file__from_path=get_test_file_path("test"))
#         instance.save()
#         self.test_patient = instance.patient
#         super(LoggedInPatientViewTestCase, self).setUp()

#     def test_list_view(self):
#         response = self.client.get(reverse("patient_list"))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "dicom/patients/patient_list.html")

#     def test_detail_view(self):
#         url = self.test_patient.get_absolute_url()
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "dicom/patients/patient_detail.html")


# class LoggedOutStudyViewTestCase(TestCase):
#     def setUp(self):
#         instance = ImageFactory(file__from_path=get_test_file_path("test"))
#         instance.save()
#         self.test_study = instance.study

#     def test_study_list_redirects_to_login(self):
#         url = reverse("dicom:study_list")
#         response = self.client.get(url, follow=True)
#         self.assertRedirects(response, f"/accounts/login/?next={url}")

#     def test_study_detail_redirects_to_login(self):
#         url = self.test_study.get_absolute_url()
#         response = self.client.get(url, follow=True)
#         self.assertRedirects(response, f"/accounts/login/?next={url}")


# class LoggedInStudyViewTestCase(LoggedInTestCase):
#     def setUp(self):
#         instance = ImageFactory(file__from_path=get_test_file_path("test"))
#         instance.save()
#         self.test_study = instance.study
#         super(LoggedInStudyViewTestCase, self).setUp()

#     def test_list_view(self):
#         response = self.client.get(reverse("dicom:study_list"))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "dicom/studies/study_list.html")

#     def test_detail_view(self):
#         url = self.test_study.get_absolute_url()
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "dicom/studies/study_detail.html")

