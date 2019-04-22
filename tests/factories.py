# import factory
# import os
# import pickle

# from django_dicom.models import Image

# TEST_FILES_PATH = os.path.abspath("./tests/files/")
# TEST_FILE = os.path.join(TEST_FILES_PATH, "001.dcm")
# TEST_DIR = os.path.join(TEST_FILES_PATH, "data")

# with open("uids/image_uids.pkl", "rb") as uids_file:
#     UIDS = pickle.load(uids_file)


# class ImageFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = Image
#         strategy = factory.BUILD_STRATEGY

#     file = factory.django.FileField()
#     uid = factory.Faker("random_element", elements=UIDS)
#     number = factory.Faker("pyint")
#     date = factory.Faker("date_this_decade", before_today=True)
#     time = factory.Faker("time_object")

#     series = factory.SubFactory("django_dicom.tests.factories.SeriesFactory")
