from django.db import models
from django_extensions.db.models import TimeStampedModel
from django_dicom.reader import HeaderInformation
from django_dicom.utils import snake_case_to_camel_case


class DicomEntity(TimeStampedModel):
    """
    An abstract model to represent a `DICOM entity`_.

    .. _DICOM entity: https://dcm4che.atlassian.net/wiki/spaces/d2/pages/1835038/A+Very+Basic+DICOM+Introduction    
    """

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
        "names": ("created", "modified"),
    }

    # This dictionary is used to convert field names to pydicom's header keywords.
    # It will be used by the derived classes to update their fields using header
    # information.
    FIELD_TO_HEADER = {}

    class Meta:
        abstract = True

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
            pydicom header keyword.
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
            The field in question.
        
        Returns
        -------
        bool
            Whether this field represent DICOM header information or not.
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
            Fields representing DICOM header information.
        """

        fields = self._meta.get_fields()
        return [field for field in fields if self.is_header_field(field)]

    def update_fields_from_header(
        self, header: HeaderInformation, exclude: list = []
    ) -> None:
        """
        Update model fields from header data. 
        
        Parameters
        ----------
        header : HeaderInformation
            DICOM header data.
        exclude : list, optional
            Field names to exclude (the default is [], which will not exclude any header fields).
        """
        fields = [
            field for field in self.get_header_fields() if field.name not in exclude
        ]
        for field in fields:
            keyword = self.get_header_keyword(field.name)
            value = header.get_value(keyword)
            setattr(self, field.name, value)
