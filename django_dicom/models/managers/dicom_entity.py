from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class DicomEntityManager(models.Manager):
    def from_header(self, header) -> tuple:
        uid = header.get_entity_uid(self.model)
        try:
            existing = self.get(uid=uid)
        except ObjectDoesNotExist:
            new_instance = self.model()
            new_instance.save(header=header)
            return new_instance, True
        else:
            return existing, False
