"""
Definition of the :class:`~django_dicom.models.dicom_entity.DicomEntity` class.
This `abstract model`_ serves as a base class for the various `DICOM entities`_
(e.g. :class:`~django_dicom.models.study.Study` and
:class:`~django_dicom.models.patient.Patient`).

.. _abstract model:
   https://docs.djangoproject.com/en/3.0/topics/db/models/#abstract-base-classes
.. _DICOM entities:
   http://dicom.nema.org/dicom/2013/output/chtml/part03/chapter_A.html

"""


import logging

from dicom_parser.header import Header as DicomHeader
from dicom_parser.utils.value_representation import ValueRepresentation
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django_dicom.models.managers.dicom_entity import DicomEntityManager
from django_dicom.models.utils import logs, snake_case_to_camel_case
from django_dicom.utils.html import Html


class DicomEntity(TimeStampedModel):
    """
    `Abstract model`_ providing common functionality for DICOM entities. For
    more information about DICOM entites, see this_ introduction.

    .. _Abstract model:
       https://docs.djangoproject.com/en/3.0/topics/db/models/#abstract-base-classes
    .. _this:
       https://dcm4che.atlassian.net/wiki/spaces/d2/pages/1835038/A+Very+Basic+DICOM+Introduction


    """

    objects = DicomEntityManager()

    #: A dictionary used to convert field names to header keywords.
    FIELD_TO_HEADER = {}

    # This dictionairy is used to identify fields that do not represent DICOM
    # header information. These fields will not be updated when calling a derived
    # model's update_fields_from_header() method.
    _NOT_HEADER_FIELD = {
        "types": (
            models.OneToOneField,
            models.ForeignKey,
            models.AutoField,
            models.ManyToOneRel,
            models.FileField,
            models.TextField,
        ),
        "names": ("created", "modified", "warnings"),
    }

    _logger = logging.getLogger("data.dicom.models")

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Log new instance creation.
        if self.pk is None:
            self.log_creation()

    def save(self, *args, **kwargs):
        """
        Overrides :meth:`~django.db.models.Model.save` to create logs and
        update the instance's fields from header information if provided.
        """

        name: str = self.__class__.__name__

        # Log save start.
        start_log: str = logs.ENTITY_SAVE_START.format(name=name)
        self._logger.debug(start_log)

        # Check for a DICOM header to update the entity's fields from.
        if "header" in kwargs:
            header: DicomHeader = kwargs.pop("header")
            self.update_fields_from_header(header)

        # Save.
        super().save(*args, **kwargs)

        # Log save end.
        end_log: str = logs.ENTITY_SAVE_END.format(name=name, pk=self.pk)
        self._logger.debug(end_log)

    def log_creation(self) -> None:
        """
        Logs the creation of a new instance of the calling Entity.

        """

        name: str = self.__class__.__name__
        log: str = logs.ENTITY_CREATION.format(name=name)
        self._logger.debug(log)

    def get_admin_link(self, text: str = None) -> str:
        """
        Returns an HTML link to this instance's page in the admin site.

        Parameters
        ----------
        text : str, optional
            Text to display, by default None

        Returns
        -------
        str
            HTML element
        """

        model_name: str = self.__class__.__name__
        return Html.admin_link(model_name, self.id, text=text)

    @property
    def admin_link(self) -> str:
        """
        Calls
        :meth:`~django_dicom.models.dicom_entity.DicomEntity.get_admin_link`
        to return a link to this instance's page in the admin site.

        Returns
        -------
        str
            HTML element
        """

        return self.get_admin_link()

    @classmethod
    def get_header_keyword(cls, field_name: str) -> str:
        """
        Returns the data element keyword to return the requested field's value from
        header data. Relies on the derived model's `FIELD_TO_HEADER` class attribute.
        If no matching key is found, will simply return the field's name in
        CamelCase formatting (the formatting of pydicom_\'s header keywords).

        .. _pydicom: https://pydicom.github.io/

        Returns
        -------
        str
            pydicom header keyword
        """

        camel_case = snake_case_to_camel_case(field_name)
        return cls.FIELD_TO_HEADER.get(field_name, camel_case)

    def is_header_field(self, field: models.Field) -> bool:
        """
        Returns a boolean indicating whether the provided field represents
        DICOM header information or not.

        Parameters
        ----------
        field : :class:`~django.db.models.Field`
            Field in question

        Returns
        -------
        bool
            Whether this field represent DICOM header information or not
        """

        valid_type = not isinstance(field, self._NOT_HEADER_FIELD["types"])
        valid_name = field.name not in self._NOT_HEADER_FIELD["names"]
        return valid_type and valid_name

    def get_header_fields(self) -> list:
        """
        Returns a list of the derived model's fields which represent DICOM header
        information.

        Returns
        -------
        list
            Fields representing DICOM header information
        """

        fields = self._meta.get_fields()
        return [field for field in fields if self.is_header_field(field)]

    def update_fields_from_header(self, header, exclude: list = None) -> None:
        """
        Update fields from header data.

        Parameters
        ----------
        header : :class:`dicom_parser.header.Header`
            DICOM header data
        exclude : list, optional
            Field names to exclude, default is []
        """

        # Log field update start.
        name: str = self.__class__.__name__
        self._logger.debug(logs.UPDATE_FIELDS_START.format(name=name))

        # Create a list of fields to read from the header.
        exclude = exclude or []
        fields = [
            field for field in self.get_header_fields() if field.name not in exclude
        ]
        # Log the result.
        self._logger.debug(f"Included fields: {[field.name for field in fields]}")
        if exclude:
            self._logger.debug(f"Excluded fields: {exclude}")

        # Update fields from header information.
        for field in fields:
            keyword = self.get_header_keyword(field.name)
            self._logger.debug(f"Querying {field.name}...")
            # Read the data element.
            try:
                data_element = header.instance.get_data_element(keyword)
            # In case the header does not contain the field's keyword:
            except KeyError:
                value = None
            else:
                value = data_element.value
                # Handle Code String data elements
                if data_element.VALUE_REPRESENTATION == ValueRepresentation.CS:
                    if data_element.value_multiplicity > 1:
                        value = [v for v in data_element.raw.value]
                    else:
                        value = data_element.raw.value
                # Listify ArrayField values
                if isinstance(field, ArrayField) and not isinstance(value, list):
                    value = [value]
            # Set the field's value and log.
            setattr(self, field.name, value)
            self._logger.debug(f"{field.name} set to {value}.")
