import os
import zipfile

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.utils import IntegrityError
from django_dicom.models.managers.dicom_entity import DicomEntityManager


class InstanceManager(DicomEntityManager):
    UID_FIELD = "instance_uid"

    def from_dcm(self, file_object):
        content = ContentFile(file_object.read())
        temp_file_name = default_storage.save("tmp.dcm", content)
        instance = self.model(file=temp_file_name)
        try:
            instance.save()
        except IntegrityError:
            # If the UID exists already, delete the temporary file and return
            # the existing instance
            temp_file_path = os.path.join(settings.MEDIA_ROOT, temp_file_name)
            uid = instance.get_entity_uid_from_headers(self.model)
            os.remove(temp_file_path)
            return self.get_by_uid(uid)
        return instance

    def from_zip(self, file):
        dest_name = default_storage.save("tmp.zip", ContentFile(file.read()))
        dest_path = os.path.join(settings.MEDIA_ROOT, dest_name)
        with zipfile.ZipFile(dest_path, "r") as archive:
            for file_name in archive.namelist():
                if file_name.endswith(".dcm"):
                    with archive.open(file_name) as dcm_file:
                        self.from_dcm(dcm_file)
        os.remove(dest_path)

    def from_local_directory(self, path: str):
        for directory, sub_directory, file_list in os.walk(path):
            for file_name in file_list:
                if file_name.endswith(".dcm"):
                    full_path = os.path.join(directory, file_name)
                    with open(full_path, "rb") as f:
                        self.from_dcm(f)
