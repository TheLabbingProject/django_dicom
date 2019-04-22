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
        Stores the DICOM file in a temporary location under `MEDIA_ROOT`_ using
        Django's `default_storage`_.

        .. _MEDIA_ROOT: https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-MEDIA_ROOT
        .. _default_storage: https://docs.djangoproject.com/en/2.2/topics/files/#file-storage
        
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

    def update_image_fields_from_header(self) -> None:
        """
        Updates the added image's fields using header information and saves.
        """

        self.image.update_fields_from_header(self.image.header)
        self.image.save()

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

    def get_or_create_entity(self, Entity: DicomEntity) -> tuple:
        """
        Gets or creates an instance of the given :class:`django_dicom.DicomEntity`
        using its UID. 
        
        Parameters
        ----------
        Entity : DicomEntity
            One of the DICOM entities (Image, Series, Study, and Patient).
        
        Returns
        -------
        tuple
            (dicom_entity, created)
        """

        uid = self.get_entity_uid_from_header(Entity)
        entity, created = Entity.objects.get_or_create(uid=uid)
        if created:
            entity.update_fields_from_header(self.image.header)
            entity.save()
        return entity

    def get_image_destination(self) -> str:
        """
        Returns the default relative path for this image under `MEDIA_ROOT`_.
        TODO: Add a way for the user to configure this.

        .. _MEDIA_ROOT: https://docs.djangoproject.com/en/2.2/ref/settings/#media-root
        
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
        Moves the created image to its default location under `MEDIA_ROOT`_.

        .. _MEDIA_ROOT: https://docs.djangoproject.com/en/2.2/ref/settings/#media-root
        
        Returns
        -------
        str
            Full path of the new location.
        """

        relative_destination = self.get_image_destination()
        destination = os.path.join(settings.MEDIA_ROOT, relative_destination)
        # Save a reference to the current path for renaming
        current_path = self.image.dcm.path
        # Changing the image's FileField value
        self.image.dcm.name = relative_destination
        # Make sure the destination directory exists
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        # Move file
        os.rename(current_path, destination)
        return destination

    def generate_entities_and_relationships(self) -> None:
        """
        Execute the generation and association of the new image's DICOM entities.
        """

        self.image = self.create_image()
        self.image.update_fields_from_header(self.image.header)
        self.image.series = self.get_or_create_entity(Series)
        self.image.series.study = self.get_or_create_entity(Study)
        self.image.series.patient = self.get_or_create_entity(Patient)
        self.image.save()

    def handle_integrity_error(self) -> tuple:
        """
        If an IntegrityError is raised during generation of the DICOM entities,
        print a warning message and delete the file and Image instance. An
        InegrityError should indicate the image already exists in the database, 
        so the method also tries to return the existing Image instance.
        
        Returns
        -------
        tuple 
            ( existing_image , created )
        """

        uid = self.image.uid
        os.remove(self.image.dcm.path)
        self.image.delete()
        return Image.objects.get(uid=uid), False

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
        except IntegrityError as e:
            print(e.args)

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
        self.move_image_to_destination()
        return self.image, True
