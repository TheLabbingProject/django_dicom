from django.db import models


class DicomEntityManager(models.Manager):
    pass
    # def get_by_uid(self, uid: str):
    #     if hasattr(self, "uid"):
    #         return self.get(uid=uid)
    #     raise NotImplementedError

    # def get_or_create_by_uid(self, uid: str):
    #     if hasattr(self, "uid"):
    #         return self.get_or_create(uid=uid)
    #     raise NotImplementedError
