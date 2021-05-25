"""
Definition of a custom :class:`~django.db.models.Manager` for the
:class:`~django_dicom.models.dicom_entity.DicomEntity` model.
"""
from typing import Tuple

from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class DicomEntityManager(models.Manager):
    """
    Custom :class:`~django.db.models.Manager` for the
    :class:`~django_dicom.models.dicom_entity.DicomEntity` model.
    """

    def from_header(self, header) -> Tuple:
        """
        Get or create an instance using the provided header.

        Parameters
        ----------
        header : :class:`django_dicom.models.header.Header`
            Header instance to query this entity's information from

        Returns
        -------
        Tuple[DicomEntity, bool]
            dicom_entity, created
        """

        uid = header.get_entity_uid(self.model)
        try:
            existing = self.get(uid=uid)
        except ObjectDoesNotExist:
            new_instance = self.model()
            new_instance.save(header=header)
            return new_instance, True
        else:
            return existing, False
