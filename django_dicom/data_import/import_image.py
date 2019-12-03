import os

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django_dicom.models import Image, Series, Study, Patient
from django_dicom.models.dicom_entity import DicomEntity
from io import BufferedReader


class ImportImage:
    """
    A class to handle importing new DICOM files to the database. Takes care of
    maintaining the Series, Study, and Patient relations with the created Image.
    """

    def __init__(self, dcm: BufferedReader):
        """
        Assigns the file data to the *dcm* attribute and declares the image attribute
        that will later be assigned the created :class:`django_dicom.Image` instance
        
        Parameters
        ----------
        dcm : BufferedReader
            Raw buffered DICOM file (*.dcm*).
        
        """

        self.dcm = dcm
        self.image = None

    def store_file(self) -> str:
        """
        Stores the DICOM file in a temporary location under `MEDIA_ROOT <https://docs.djangoproject.com/en/2.2/ref/settings/#media-root>`_ 
        using Django's `default_storage <https://docs.djangoproject.com/en/2.2/topics/files/#file-storage>`_.
        
        Returns
        -------
        str
            The name of the temporary file created.
        """

        content = ContentFile(self.dcm.read())
        return default_storage.save("tmp.dcm", content)

    def create_image(self) -> Image:
        """
        Stores the DICOM file locally and creates an Image instance from it without
        saving it (allowing for the fields to be updated from the header beforehand).
        
        Returns
        -------
        Image
            The created Image for the given file.
        """

        temp_file_name = self.store_file()
        return Image(dcm=temp_file_name)

    def get_entity_uid_from_header(self, Entity: DicomEntity) -> str:
        """
        Returns the UID of the given entity from the DICOM header information.
        
        Parameters
        ----------
        Entity : DicomEntity
            One of the DICOM entities (Image, Series, Study, and Patient).
        
        Returns
        -------
        str
            The UID value for the given entity.
        """

        keyword = Entity.get_header_keyword("uid")
        return self.image.header.get_value(keyword)

    def get_or_create_entity(self, Entity: DicomEntity, save: bool = True) -> tuple:
        """
        Gets or creates an instance of the given :class:`django_dicom.DicomEntity`
        using its UID. 
        The *save* parameter is mostly meant to help with testing.
        
        Parameters
        ----------
        Entity : DicomEntity
            One of the DICOM entities (Image, Series, Study, and Patient).
        save : bool
            Whether to save the instance to the database if it is created (default to True, which will call the save() method).
        
        Returns
        -------
        tuple
            (dicom_entity, created)
        """

        uid = self.get_entity_uid_from_header(Entity)
        try:
            return Entity.objects.get(uid=uid), False
        except ObjectDoesNotExist:
            entity = Entity(uid=uid)
            entity.update_fields_from_header(self.image.header)
            if save:
                entity.save()
            return entity, True

    def get_image_destination(self) -> str:
        """
        Returns the default relative path for this image under `MEDIA_ROOT <https://docs.djangoproject.com/en/2.2/ref/settings/#media-root>`_.
        TODO: Add a way for the user to configure this.
        
        Returns
        -------
        str
            Default relative path for this image.
        """

        patient_uid = self.get_entity_uid_from_header(Patient)
        series_uid = self.get_entity_uid_from_header(Series)
        name = f"{self.image.number}.dcm"
        return os.path.join("MRI", patient_uid, series_uid, "DICOM", name)

    def move_image_to_destination(self) -> str:
        """
        Moves the created image to its default location under `MEDIA_ROOT <https://docs.djangoproject.com/en/2.2/ref/settings/#media-root>`_.
        
        Returns
        -------
        str
            Full path of the new location.
        """

        relative_destination = self.get_image_destination()
        destination = os.path.join(settings.MEDIA_ROOT, relative_destination)
        current_path = self.image.dcm.path
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        os.rename(current_path, destination)
        return relative_destination

    def generate_entities_and_relationships(self) -> None:
        """
        Execute the generation and association of the new image's DICOM entities.
        """

        self.image = self.create_image()
        self.image.update_fields_from_header(self.image.header)

        # We create the Series instance but avoid saving if it was created in
        # order to have a chance to first set its patient and study fields.
        series, created_series = self.get_or_create_entity(Series, save=False)
        if created_series or not all([series.study, series.patient]):
            # If the instance was created, we get or create the appropriate
            # Patient and Study instances and set the created instance's fields.
            patient, _ = self.get_or_create_entity(Patient)
            study, _ = self.get_or_create_entity(Study)
            series.patient = patient
            series.study = study
            series.save()

        # Finally we can relate the Series instance to the created Image instance and save.
        self.image.series = series
        self.image.save()

    def handle_integrity_error(self) -> tuple:
        """
        If an IntegrityError is raised during generation of the DICOM entities,
        delete the temporary file.
        An InegrityError should indicate the image already exists in the database,
        so the method also tries to return the existing Image instance.
        
        Returns
        -------
        tuple
            ( existing_image , created )
        """

        os.remove(self.image.dcm.path)
        return Image.objects.get(uid=self.image.uid), False

    def run(self) -> tuple:
        """
        Adds the image to the database and generates its associated entities as
        an atomic transaction. If the transaction fails, calls :meth:`~django_dicom.data_import.import_image.ImportImage.handle_integrity_error`
        This assumes an existing image and tries to return it.
        
        Returns
        -------
        tuple
            ( image_instance, created )
        """
        try:
            with transaction.atomic():
                self.generate_entities_and_relationships()

        # An IntegrityError should indicate the image exists in the database.
        except IntegrityError:

            # Assume image exists in database and returns it.
            try:
                return self.handle_integrity_error()

            # If this assumption was wrong, handle_integity_error() will raise an
            # ObjectDoesNotExist, and in that case we re-raise the original IntegrityError.
            except ObjectDoesNotExist:
                pass
            raise

        # If we got here, the transaction must have been successful, so we move the
        # dcm file to its desired location in the file-system and return it.
        self.image.dcm.name = self.move_image_to_destination()
        self.image.save()
        return self.image, True
