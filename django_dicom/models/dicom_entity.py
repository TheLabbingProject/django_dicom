import logging

from dicom_parser.utils.value_representation import ValueRepresentation
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django_dicom.models import logs
from django_dicom.models.managers.dicom_entity import DicomEntityManager
from django_dicom.models.utils import snake_case_to_camel_case
from django_dicom.utils.html import Html


class DicomEntity(TimeStampedModel):
    """
    An abstract model to represent a `DICOM entity`_.

    .. _DICOM entity: https://dcm4che.atlassian.net/wiki/spaces/d2/pages/1835038/A+Very+Basic+DICOM+Introduction
    """

    objects = DicomEntityManager()

    # This dictionairy is used to identify fields that do not represent DICOM
    # header information. These fields will not be updated when calling a derived
    # model's update_fields_from_header() method.
    NOT_HEADER_FIELD = {
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

    # This dictionary is used to convert field names to pydicom's header keywords.
    # It will be used by the derived classes to update their fields using header
    # information.
    FIELD_TO_HEADER = {}

    logger = logging.getLogger("data.dicom.models")

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Log new instance creation.
        if self.pk is None:
            self.log_creation()

    def save(self, *args, **kwargs):
        name = self.__class__.__name__

        # Log save start.
        start_log = logs.ENTITY_SAVE_START.format(name=name)
        self.logger.debug(start_log)

        if "header" in kwargs:
            header = kwargs.pop("header")
            self.update_fields_from_header(header)

        # Save.
        super().save(*args, **kwargs)

        # Log save end.
        end_log = logs.ENTITY_SAVE_END.format(name=name, pk=self.pk)
        self.logger.debug(end_log)

    def log_creation(self) -> None:
        """
        Logs the creation of a new instance of the calling Entity.

        """

        name = self.__class__.__name__
        log = logs.ENTITY_CREATION.format(name=name)
        self.logger.debug(log)

    def get_admin_link(self, text: str = None) -> str:
        model_name = self.__class__.__name__
        return Html.admin_link(model_name, self.id, text=text)

    @property
    def admin_link(self) -> str:
        return self.get_admin_link()

    @classmethod
    def get_header_keyword(cls, field_name: str) -> str:
        """
        Returns the pydicom keyword to return the requested field's value from
        header data. Relies on the derived model's `FIELD_TO_HEADER` class attribute.
        If no matching key is found, will simply return the field's name in
        CamelCase formatting (the formatting of pydicom's header keywords).

        Returns
        -------
        str
            pydicom header keyword
        """

        camel_case = snake_case_to_camel_case(field_name)
        return cls.FIELD_TO_HEADER.get(field_name, camel_case)

    def is_header_field(self, field: models.Field) -> bool:
        """
        Returns a boolean indicating whether this field represents DICOM header
        information or not.

        Parameters
        ----------
        field : models.Field
            Field in question

        Returns
        -------
        bool
            Whether this field represent DICOM header information or not
        """

        valid_type = not isinstance(field, self.NOT_HEADER_FIELD["types"])
        valid_name = field.name not in self.NOT_HEADER_FIELD["names"]
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
        Update model fields from header data.

        Parameters
        ----------
        header : :class:`~dicom_parser.header.Header`
            DICOM header data
        exclude : list, optional
            Field names to exclude (the default is [], which will not exclude any header
            fields)
        """

        name = self.__class__.__name__
        self.logger.debug(logs.UPDATE_FIELDS_START.format(name=name))
        exclude = exclude or []
        fields = [
            field for field in self.get_header_fields() if field.name not in exclude
        ]
        self.logger.debug(f"Included fields: {[field.name for field in fields]}")
        if exclude:
            self.logger.debug(f"Excluded fields: {exclude}")

        for field in fields:
            keyword = self.get_header_keyword(field.name)
            self.logger.debug(f"Querying {field.name}...")
            try:
                data_element = header.instance.get_data_element(keyword)
            except KeyError:
                value = None
            else:
                value = data_element.value
                if data_element.VALUE_REPRESENTATION == ValueRepresentation.CS:
                    if data_element.value_multiplicity > 1:
                        value = [v for v in data_element.raw.value]
                    else:
                        value = data_element.raw.value
                if isinstance(field, ArrayField) and not isinstance(value, list):
                    value = [value]
            setattr(self, field.name, value)
            self.logger.debug(f"{field.name} set to {value}.")
