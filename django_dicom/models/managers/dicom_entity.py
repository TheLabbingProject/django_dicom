from django.db import models


class DicomEntityManager(models.Manager):
    UID_FIELD = None

    def get_by_uid(self, uid: str):
        if self.UID_FIELD:
            return self.get(**{self.UID_FIELD: uid})
        raise NotImplementedError

    def get_or_create_by_uid(self, uid: str):
        if self.UID_FIELD:
            return self.get_or_create(**{self.UID_FIELD: uid})
        raise NotImplementedError
